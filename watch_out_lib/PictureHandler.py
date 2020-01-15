from watch_out_lib.Config import *
from watch_out_lib.MyLogger import logger, get_trace
from watch_out_lib.TimeTracker import time_tracker
from watch_out_lib.WatchOutSettings import WatchOutSettings
from watch_out_lib.BackupFileExpiryHandler import FileExpiryHandler

import datetime
import os
import signal
import shutil
import stat
import subprocess
import sys

SHOULD_EXIST = True
SHOULD_NOT_EXIST = False


# TODO: Would need a config file locking context manager during picture uploading
# TODO: to avoid corrupting members

class PictureHandler:
    def __init__(self, args, config, data_cap_handler):
        self._verbose = args.verbosity
        self._config = config
        self._data_cap_handler = data_cap_handler
        self._watch_out_settings = WatchOutSettings.get_singleton()
        self._password = args.camera_password

        self._backup_folder_date_path = None
        self._backup_sub_folder_time_path = None

        self._public_pictures_removed_flag = False

        if not os.path.isdir(self._watch_out_settings.temp_pictures_path):
            os.makedirs(self._watch_out_settings.temp_pictures_path)

        self._backup_files = FileExpiryHandler(self._watch_out_settings.backup_pictures_root_path,
                                               parent=None,
                                               level=FileExpiryHandler.ROOT_FOLDER)
        self._init_backup_files()
        self._master_enabled_output_files = None

        self._last_pic_upload_time = {}
        for pic_type in PARAM_PICTURE_TYPE_LIST:
            self._last_pic_upload_time[pic_type] = {}
            for cam_index in range(0, DEFAULT_NUMBER_OF_CAMERAS):
                self._last_pic_upload_time[pic_type][cam_index] = None

    def run(self):
        self._cleanup()

        # Upload picture in atomic way to avoid configurator
        # to corrupt picture settings while uploading
        try:
            # self._config.lock()
            self._update_time_based_members()
            self._set_master_enabled_pictures()
            self._check_data_cap_reached_picture()
            if not self._data_cap_handler.data_cap_reached():
                self._check_upload()
        finally:
            # self._config.unlock()
            pass

    def _update_time_based_members(self):
        today_s_date_str = time_tracker.current_time.strftime(self._backup_files.backup_folder_date_format)
        self._backup_folder_date_path = self._watch_out_settings.backup_pictures_root_path.joinpath(today_s_date_str)

        current_hour_str = "%s" % time_tracker.current_time.strftime(self._backup_files.backup_folder_time_format)
        self._backup_sub_folder_time_path = self._backup_folder_date_path.joinpath(current_hour_str)

    def _set_master_enabled_pictures(self):
        self._master_enabled_output_files = dict()
        for pic_type in PARAM_PICTURE_TYPE_LIST:
            self._master_enabled_output_files[pic_type] = dict()
            for cam_index in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
                if self._config.get(OPTION_PICTURE_UPLOAD_ENABLE, picture_type=pic_type, cam_index=cam_index):
                    self._master_enabled_output_files[pic_type][cam_index] = self._get_output_file(pic_type, cam_index)

    def _check_upload(self):
        backup_folder_check = False
        pictures_uploaded = False

        for pic_type in self._master_enabled_output_files:
            for cam_index in self._master_enabled_output_files[pic_type]:
                if self._pic_upload_scheduled_enabled(pic_type, cam_index):
                    if not backup_folder_check and pic_type == PARAM_PICTURE_TYPE_BACKUP:
                        self._check_for_new_backup_folder()
                        backup_folder_check = True

                    upload_interval = self._config.get(OPTION_PICTURE_UPLOAD_INTERVAL_TIME_DELTA, picture_type=pic_type, cam_index=cam_index)
                    if self._last_pic_upload_time[pic_type][cam_index] is None or \
                            time_tracker.current_time - self._last_pic_upload_time[pic_type][cam_index] >= upload_interval:
                        self._extract_and_upload(pic_type, cam_index)
                        pictures_uploaded = True

        if pictures_uploaded:
            self._data_cap_handler.update_config_data_usage()

    @staticmethod
    def _get_date(d, t):
        return datetime.datetime(year=d.year,
                                 month=d.month,
                                 day=d.day,
                                 hour=t.hour,
                                 minute=t.minute,
                                 second=0)

    def _pic_upload_scheduled_enabled(self, pic_type, cam_index):
        # TODO: Could span one thread for each camera instead of looping around and rename camera handler?
        pic_master_upload_enable = self._config.get(OPTION_PICTURE_UPLOAD_ENABLE, picture_type=pic_type, cam_index=cam_index)
        if not pic_master_upload_enable:
            return False
        upload_start_time = self._config.get(OPTION_PICTURE_UPLOAD_START_TIME, picture_type=pic_type, cam_index=cam_index)
        upload_stop_time = self._config.get(OPTION_PICTURE_UPLOAD_STOP_TIME, picture_type=pic_type, cam_index=cam_index)

        upload_start_date = self._get_date(time_tracker.current_time, upload_start_time)
        upload_stop_date = self._get_date(time_tracker.current_time, upload_stop_time)

        if (time_tracker.current_time >= upload_start_date) and \
                (time_tracker.current_time < upload_stop_date):
            # TODO: entered flags per picture so we can print these messages without hosing the console
            # if not self._public_picture_upload_schedule_enable[pic_type][cam_index]:
            #     logger.debug("Entering picture upload schedule for %s %d" % (pic_type, cam_index))
            return True
        else:
            # if self._public_picture_upload_schedule_enable[pic_type][cam_index]:
            #     logger.debug("Exiting picture upload schedule for %s %d" % (pic_type, cam_index))
            return False

    def _get_output_file(self, pic_type, cam_index):
        cam_name = self._config.get(OPTION_CAMERA_DESCRIPTION, picture_type=pic_type, cam_index=cam_index)
        cam_name = cam_name.replace(" ", "_")
        if pic_type == PARAM_PICTURE_TYPE_BACKUP:
            pic_index_str = time_tracker.current_time.strftime(self._backup_files.time_ms_format)
            picture_name = "%s.%s.%s" % (cam_name,
                                         pic_index_str,
                                         self._watch_out_settings.ffmpeg_output_format)
            output_file = self._backup_sub_folder_time_path.joinpath(picture_name)
        else:
            picture_name = "%s.%s" % (cam_name,
                                      self._watch_out_settings.ffmpeg_output_format)
            output_file = self._watch_out_settings.temp_pictures_path.joinpath(picture_name)

        return str(output_file)

    def _extract_and_upload(self, pic_type, cam_index):
        output_file = self._master_enabled_output_files[pic_type][cam_index]

        pix_format = self._config.get(OPTION_PICTURE_FORMAT, picture_type=pic_type, cam_index=cam_index)
        grayscale_en = self._config.get(OPTION_PICTURE_GRAYSCALE, picture_type=pic_type, cam_index=cam_index)
        quality = self._config.get(OPTION_PICTURE_QUALITY, picture_type=pic_type, cam_index=cam_index)
        resolution = self._config.get(OPTION_PICTURE_RESOLUTION, picture_type=pic_type, cam_index=cam_index)
        camera_url_format_str = self._config.get(OPTION_CAMERA_URL, picture_type=pic_type, cam_index=cam_index)
        camera_protocol = self._config.get(OPTION_CAMERA_PROTOCOL, picture_type=pic_type, cam_index=cam_index)

        grayscale_arg = ""
        if grayscale_en:
            grayscale_arg = ",format=gray"

        try:
            if self._password == "":
                try:
                    camera_url = camera_url_format_str.format(camera_index=cam_index)
                except KeyError:
                    camera_url = camera_url_format_str
            else:
                try:
                    camera_url = camera_url_format_str.format(password=self._password,
                                                              camera_index=cam_index)
                except KeyError:
                    camera_url = camera_url_format_str.format(password=self._password)

            ffmpeg_base_command = self._watch_out_settings.ffmpeg_base_command.format(protocol=camera_protocol,
                                                                                      camera_url=camera_url)

            ffmpeg_command = self._watch_out_settings.ffmpeg_command_format_string.format(ffmpeg_base_command=ffmpeg_base_command,
                                                                                          quality=quality,
                                                                                          resolution=resolution,
                                                                                          grayscale=grayscale_arg,
                                                                                          pix_fmt=pix_format,
                                                                                          output_file=output_file)
            logger.debug("Uploading picture: Time: %s Cam Index: %d Cam type: %s" % (str(time_tracker.current_time), cam_index, pic_type), 2)
        except KeyError as e:
            msg = get_trace(e)
            logger.warning(msg)
            sys.exit(1)

        self._run_command(ffmpeg_command)
        try:
            self._data_cap_handler.add_usage(os.path.getsize(output_file))
            if pic_type == PARAM_PICTURE_TYPE_BACKUP:
                self._backup_files.add_picture(output_file, self._config.get(OPTION_PICTURE_EXPIRY_TIME_DELTA,
                                                                             cam_index=cam_index,
                                                                             picture_type=PARAM_PICTURE_TYPE_BACKUP))
            self._last_pic_upload_time[pic_type][cam_index] = time_tracker.current_time
        except FileNotFoundError:
            logger.warning("Couldn't account for data usage of picture %s %d" % (pic_type, cam_index))

    def _run_command(self, command):
        # On windows, it seems that the subprocess can mess around with stdout/stderr,
        # save and restore after command execution.
        err = sys.stderr
        out = sys.stdout
        if self._verbose >= 1:
            logger.debug("FFMPEG COMMAND: %s" % command)
        if self._verbose >= 3:
            p = subprocess.Popen(command, shell=True)
        else:
            p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)

        timeout_flag = False
        exception = None
        try:
            o, e = p.communicate(timeout=int(self._config.get(OPTION_FFMPEG_TIMEOUT)))
        except subprocess.TimeoutExpired:
            timeout_flag = True
            o = ""
        except Exception as e:
            exception = e
        finally:
            sys.stderr = err
            sys.stdout = out

        if timeout_flag:
            logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!")
            logger.debug("FFMPEG command timed out!")
            logger.debug("!!!!!!!!!!!!!!!!!!!!!!!!!")
            try:
                p.send_signal(signal.SIGTERM)
            except:
                pass
        elif p.returncode != 0:
            if exception is not None:
                logger.error(str(e))
            else:
                o = o.decode('utf-8').replace("\r", "")
                for line in o.split("\n"):
                    logger.error(line)

    def _check_data_cap_reached_picture(self):
        should_exist = self._data_cap_handler.data_cap_reached()

        for pic_type in self._master_enabled_output_files:
            for cam_index in self._master_enabled_output_files[pic_type]:
                output_file = self._master_enabled_output_files[pic_type][cam_index]
                # Replace filename so we don't copy bunch of data cap reached files under backup
                output_file = os.path.join(os.path.dirname(output_file), self._watch_out_settings.data_cap_reached_picture_name)
                if not os.path.exists(output_file) and should_exist:
                    # If directory doesn't exist, just continue
                    if not os.path.isdir(os.path.dirname(output_file)):
                        continue
                    shutil.copyfile(self._watch_out_settings.data_cap_reached_picture_path, output_file)

    def _check_for_new_backup_folder(self):
        # No need to create new folder if data cap is reached
        if self._data_cap_handler.data_cap_reached():
            self._backup_files.print_debug()
            return

        # Create storage folder for today's backup pictures
        if not os.path.exists(self._backup_sub_folder_time_path):
            logger.debug("Creating new backup folder: %s" % str(self._backup_sub_folder_time_path))
            os.makedirs(self._backup_sub_folder_time_path)

        if not self._backup_files.exists(self._backup_folder_date_path):
            h = self._backup_files.add_child(self._backup_folder_date_path, level=FileExpiryHandler.DATE_FOLDER)
            h.add_child(self._backup_sub_folder_time_path, level=FileExpiryHandler.HOUR_FOLDER)
        else:
            date_handler = self._backup_files.get_child(self._backup_folder_date_path)
            if not date_handler.exists(self._backup_sub_folder_time_path):
                date_handler.add_child(self._backup_sub_folder_time_path, level=FileExpiryHandler.HOUR_FOLDER)

    ##########################################
    # Picture expiry management
    ##########################################
    def _cleanup(self):
        self._cleanup_temp()
        self._cleanup_backup()

    def _cleanup_temp(self):
        if not self._data_cap_handler.data_cap_reached():
            self._public_pictures_removed_flag = False
            return

        if not self._public_pictures_removed_flag:
            # We've reached the data cap allowed, stop uploading
            # Delete pics from public folder
            logger.debug("************************************************")
            logger.debug("Data cap reached, removing public pictures!")
            logger.debug("************************************************")
            for cam_index in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
                cam_name = self._config.get(OPTION_CAMERA_DESCRIPTION, picture_type=PARAM_PICTURE_TYPE_TEMP, cam_index=cam_index)
                cam_name = cam_name.replace(' ', '_')
                output_file = self._watch_out_settings.temp_pictures_path.joinpath("%s.%s" % (cam_name, self._watch_out_settings.ffmpeg_output_format))
                if os.path.exists(output_file):
                    try:
                        os.chmod(str(output_file), stat.S_IWRITE)
                        os.remove(output_file)
                    except Exception as e:
                        m = get_trace(e)
                        logger.debug("Couldn't remove %s\n%s" % (str(output_file), m))
            self._public_pictures_removed_flag = True

    def _find_longest_expiry_delta(self):
        longest_delta = None
        for cam_index in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            for picture_type in PARAM_PICTURE_TYPE_LIST:
                picture_expiry_delta = self._config.get(OPTION_PICTURE_EXPIRY_TIME_DELTA,
                                                        cam_index=cam_index,
                                                        picture_type=picture_type)
                if longest_delta is None:
                    longest_delta = picture_expiry_delta
                elif picture_expiry_delta > longest_delta:
                    longest_delta = picture_expiry_delta

        if longest_delta is None:
            raise Exception("Couldn't find longest expiry delta")

        return longest_delta

    def _init_backup_files(self):
        longest_expiry_delta = self._find_longest_expiry_delta()
        FileExpiryHandler.set_longest_expiry_delta(longest_expiry_delta)
        self._backup_files.set_children()

        # Backup paths
        today_s_date_str = time_tracker.current_time.strftime(self._backup_files.backup_folder_date_format)
        self._backup_folder_date_path = self._watch_out_settings.backup_pictures_root_path.joinpath(today_s_date_str)
        current_hour_str = "%s" % time_tracker.current_time.strftime(self._backup_files.backup_folder_time_format)
        self._backup_sub_folder_time_path = self._backup_folder_date_path.joinpath(current_hour_str)

    def _cleanup_backup(self):
        """
        Check hourly for deleting expired backup folders
        """
        if not time_tracker.hour_changed():
            return

        self._backup_files.process_expiry()
