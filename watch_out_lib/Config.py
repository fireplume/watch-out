from watch_out_lib.MyLogger import logger
import watch_out_lib.MyLogger

import datetime
import os
from pathlib import Path
import pickle
import sys

######################################################
# CONSTANTS
######################################################
CONFIG_FILE = Path(os.path.dirname(__file__)).joinpath("watch_out.pickle.cfg")

GREEN_STYLE_BG = "background-color: rgb(170, 255, 170);"
BLUE_STYLE_BG = "background-color: rgb(170, 170, 255);"
YELLOW_STYLE_BG = "background-color: rgb(255, 255, 170);"
RED_STYLE_BG = "background-color: rgba(255, 170, 170, 200);"
LIGHT_BROWN_STYLE_BG = "background-color: rgb(255, 230, 130);"
# APP_COLOR_BG = "background-color: rgb(220, 255, 220);" # Light green
# APP_COLOR_BG = "background-color: rgb(180, 180, 180);" # Gray
APP_COLOR_BG = "background-color: rgb(200, 200, 120);"  # Khaki

GRADIENT_GREEN_BLUE_BG = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(200, 255, 200, 255), stop:1 rgba(200, 200, 255, 255));"
GRADIENT_GREEN_YELLOW_BG = "background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(200, 255, 200, 255), stop:1 rgba(255, 255, 200, 255));"

RES_2560_1600 = "2560x1600"
RES_1980x1020 = "1920x1080"
RES_1600x1200 = "1600x1200"
RES_1280x720 = "1280x720"
RES_640x480 = "640x480"
RESOLUTION_LIST = [RES_2560_1600,
                   RES_1980x1020,
                   RES_1600x1200,
                   RES_1280x720,
                   RES_640x480]

FORMAT_9BPP_YUV410P = "yuv410p"
FORMAT_12BPP_YUVJ420P = "yuvj420p"
FORMAT_12BPP_YUV420P = "yuv420p"  # restricted range
FORMAT_16BPP_YUV422P = "yuv422p"
FORMAT_24BPP_YUV444P = "yuv444p"
FORMAT_32BPP_ARGB = "argb"
FORMAT_LIST = [FORMAT_9BPP_YUV410P,
               FORMAT_12BPP_YUVJ420P,
               FORMAT_12BPP_YUV420P,
               FORMAT_16BPP_YUV422P,
               FORMAT_24BPP_YUV444P,
               FORMAT_32BPP_ARGB]

TIME_HM_FORMAT = "%Hh%Mm"
TIME_MS_FORMAT = "%Mm%Ss"

PROTOCOL_UDP = 'udp'
PROTOCOL_TCP = 'tcp'

######################################################
# DEFAULTS
######################################################
# Number of cameras in your system
DEFAULT_NUMBER_OF_CAMERAS = 8
DEFAULT_MONTHLY_DATA_ALLOWANCE_GB = 8
# Should be a multiple of 32, min 32, max 512
DEFAULT_UPLOAD_STOP_MARGIN_MB = 128
DEFAULT_UPLOAD_INTERVAL_SECONDS = 300
# Time before we kil ffmpeg if it froze (ffmpeg is the utility grabbing the video stream
# and converting to picture. It's ok to kill it when it takes too much time.
# I advise against reducing this value below 5 seconds.
DEFAULT_FFMPEG_TIMEOUT = 15

DEFAULT_CAMERA_DESCRIPTION = "Camera {:d}"
DEFAULT_CAMERA_URL = "rtsp://admin:{password:s}@<ip_address>:554/ch0{camera_index:d}/0"
DEFAULT_CAMERA_PROTOCOL = PROTOCOL_TCP
DEFAULT_PICTURE_UPLOAD_START = datetime.time(hour=8, minute=0)
DEFAULT_PICTURE_UPLOAD_STOP = datetime.time(hour=17, minute=0)
DEFAULT_PICTURE_RESOLUTION = RES_1980x1020
DEFAULT_PICTURE_FORMAT = FORMAT_12BPP_YUV420P
DEFAULT_PICTURE_GRAYSCALE = True
DEFAULT_PICTURE_UPLOAD_INTERVAL_TIME_DELTA = datetime.timedelta(minutes=5)
DEFAULT_PICTURE_QUALITY = 10  # Quality within 2:best to 31:worst
DEFAULT_BACKUP_PICTURE_EXPIRY_TIME_DELTA = datetime.timedelta(days=7)
DEFAULT_PICTURE_UPLOAD_ENABLE = False

######################################################
# OPTIONS
######################################################
# Consistency options
OPTION_CURRENT_MONTH_RESET = "current_month_reset"

# Main Ui Config option
OPTION_MONTHLY_DATA_ALLOWANCE_GB = "monthly_data_allowance_gb"
OPTION_DAY_OF_MONTH_DATA_CAP_RESET = "day_of_month_data_cap_reset"
OPTION_CURRENT_MONTH_DATA_USAGE_KB = "current_month_data_usage_kb"
OPTION_UPLOAD_STOP_MARGIN_MB = "upload_stop_margin_MB"
OPTION_FFMPEG_TIMEOUT = "ffmpeg_timeout"
OPTION_LAST_DATA_CAP_RESET_DATE = "last_data_cap_reset_date"
# Include all options above:
GENERAL_OPTIONS_LIST = [OPTION_MONTHLY_DATA_ALLOWANCE_GB,
                        OPTION_DAY_OF_MONTH_DATA_CAP_RESET,
                        OPTION_CURRENT_MONTH_DATA_USAGE_KB,
                        OPTION_UPLOAD_STOP_MARGIN_MB,
                        OPTION_FFMPEG_TIMEOUT,
                        OPTION_LAST_DATA_CAP_RESET_DATE,
                        OPTION_CURRENT_MONTH_RESET]
######################################################
# Picture options
OPTION_CAMERA_DESCRIPTION = "description"
OPTION_CAMERA_URL = "camera_url"
OPTION_CAMERA_PROTOCOL = "camera_protocol"
OPTION_PICTURE_UPLOAD_START_TIME = "upload_start"
OPTION_PICTURE_UPLOAD_STOP_TIME = "upload_stop"
OPTION_PICTURE_RESOLUTION = "resolution"
OPTION_PICTURE_FORMAT = "format"
OPTION_PICTURE_GRAYSCALE = "grayscale_en"
OPTION_PICTURE_UPLOAD_INTERVAL_TIME_DELTA = "upload_interval"
OPTION_PICTURE_QUALITY = "quality"
OPTION_PICTURE_EXPIRY_TIME_DELTA = "expiry"
OPTION_PICTURE_UPLOAD_ENABLE = "enable"
# Include all option above:
PICTURE_OPTION_LIST = [OPTION_CAMERA_DESCRIPTION,  # same for all upload types...
                       OPTION_CAMERA_URL,
                       OPTION_CAMERA_PROTOCOL,
                       OPTION_PICTURE_UPLOAD_START_TIME,
                       OPTION_PICTURE_UPLOAD_STOP_TIME,
                       OPTION_PICTURE_RESOLUTION,
                       OPTION_PICTURE_FORMAT,
                       OPTION_PICTURE_GRAYSCALE,
                       OPTION_PICTURE_UPLOAD_INTERVAL_TIME_DELTA,
                       OPTION_PICTURE_QUALITY,
                       OPTION_PICTURE_EXPIRY_TIME_DELTA,
                       OPTION_PICTURE_UPLOAD_ENABLE]
######################################################
DEFAULT_PICTURE_SETTINGS_MAP = {
    OPTION_CAMERA_DESCRIPTION: DEFAULT_CAMERA_DESCRIPTION,
    OPTION_CAMERA_URL: DEFAULT_CAMERA_URL,
    OPTION_CAMERA_PROTOCOL: DEFAULT_CAMERA_PROTOCOL,
    OPTION_PICTURE_UPLOAD_START_TIME: DEFAULT_PICTURE_UPLOAD_START,
    OPTION_PICTURE_UPLOAD_STOP_TIME: DEFAULT_PICTURE_UPLOAD_STOP,
    OPTION_PICTURE_RESOLUTION: DEFAULT_PICTURE_RESOLUTION,
    OPTION_PICTURE_FORMAT: DEFAULT_PICTURE_FORMAT,
    OPTION_PICTURE_GRAYSCALE: DEFAULT_PICTURE_GRAYSCALE,
    OPTION_PICTURE_UPLOAD_INTERVAL_TIME_DELTA: DEFAULT_PICTURE_UPLOAD_INTERVAL_TIME_DELTA,
    OPTION_PICTURE_QUALITY: DEFAULT_PICTURE_QUALITY,
    OPTION_PICTURE_EXPIRY_TIME_DELTA: DEFAULT_BACKUP_PICTURE_EXPIRY_TIME_DELTA,
    OPTION_PICTURE_UPLOAD_ENABLE: DEFAULT_PICTURE_UPLOAD_ENABLE
}
######################################################
# All picture options (note that it also is used for WidgetAllPictureSettings member!)
PARAM_PICTURE_TYPE_TEMP = 'Snapshot_Picture_Upload_Settings'
PARAM_PICTURE_TYPE_BACKUP = 'Backup_Picture_Upload_Settings'
# Include all param above:
PARAM_PICTURE_TYPE_LIST = [PARAM_PICTURE_TYPE_TEMP,
                           PARAM_PICTURE_TYPE_BACKUP]


######################################################


class ConfigPictureUploadSettings:
    def __init__(self, camera_index):
        self.camera_index = camera_index
        for opt in PICTURE_OPTION_LIST:
            if opt == OPTION_CAMERA_DESCRIPTION:
                setattr(self, opt, DEFAULT_PICTURE_SETTINGS_MAP[opt].format(self.camera_index))
            else:
                setattr(self, opt, DEFAULT_PICTURE_SETTINGS_MAP[opt])


class ConfigAllPictureUploadSettings:
    def __init__(self, camera_index):
        for pic_type in PARAM_PICTURE_TYPE_LIST:
            setattr(self, pic_type, ConfigPictureUploadSettings(camera_index))


CONFIG_LOG_THRESHOLD = 3


class Config:
    def __init__(self):
        self._config_map = {OPTION_CURRENT_MONTH_RESET: False}
        if os.path.exists(CONFIG_FILE):
            self.read()
        else:
            self._create_config_default()

    def get_config_map(self):
        import copy
        return copy.copy(self._config_map)

    def read(self, option=None, **kwargs):
        # Sometimes, file might be locked, give it a few try.
        # If it is locked, there is already a sleep period, no
        # need for sleeping between attempts.
        for i in range(0, 5):
            try:
                with open(CONFIG_FILE, 'rb') as fd:
                    tmp = pickle.load(fd)
                    if option is None:
                        self._config_map = tmp.get_config_map()
                    else:
                        return tmp.get(option, **kwargs)
                    break
            except PermissionError as e:
                if i == 4:
                    raise e

    def write(self, option=None, value=None, **kwargs):
        if option is None:
            if 'skip_log' not in kwargs:
                logger.debug("###########################")
                logger.debug("WRITE CONFIG FILE")
                logger.debug("###########################")
        else:
            logger.debug("********************************")
            logger.debug("Writing directly to config file: %s" % option)
            logger.debug("********************************")

        if option is None:
            with open(CONFIG_FILE, 'wb') as fd:
                file_size = os.path.getsize(CONFIG_FILE)
                if sys.platform == 'linux':
                    import fcntl
                    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    pickle.dump(self, fd)
                    fcntl.flock(fd, fcntl.LOCK_UN)
                elif sys.platform == 'win32':
                    import msvcrt
                    msvcrt.locking(fd.fileno(), msvcrt.LK_RLCK, file_size)
                    pickle.dump(self, fd)
                    msvcrt.locking(fd.fileno(), msvcrt.LK_UNLCK, file_size)
                else:
                    raise Exception("%s platform not supported" % sys.platform)
        elif value is not None:
            self.read()
            self.set(option, value, **kwargs)
            self.write(skip_log=True)

    def _create_config_default(self):
        logger.debug("###########################")
        logger.debug("_create_config_default CONFIG FILE")
        logger.debug("###########################")
        self._config_map[OPTION_CURRENT_MONTH_RESET] = False

        for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            self._config_map[i] = ConfigAllPictureUploadSettings(i)

        self.set(OPTION_MONTHLY_DATA_ALLOWANCE_GB,
                 DEFAULT_MONTHLY_DATA_ALLOWANCE_GB)

        self.set(OPTION_DAY_OF_MONTH_DATA_CAP_RESET,
                 datetime.datetime.today().day)

        self.set(OPTION_CURRENT_MONTH_DATA_USAGE_KB,
                 0)

        self.set(OPTION_UPLOAD_STOP_MARGIN_MB,
                 DEFAULT_UPLOAD_STOP_MARGIN_MB)

        self.set(OPTION_FFMPEG_TIMEOUT,
                 DEFAULT_FFMPEG_TIMEOUT)

        self.set(OPTION_LAST_DATA_CAP_RESET_DATE,
                 datetime.datetime.today())

        self.write()

    def set(self, option, value, **kwargs):
        """
        If processing a picture option, the following keyword parameter must be set:
            'picture_type': either PARAM_PICTURE_TYPE_TEMP or PARAM_PICTURE_TYPE_BACKUP
            'cam_index': camera index for which to modify the option
        """
        logger.debug("Config.set:", CONFIG_LOG_THRESHOLD)
        logger.debug("   %s -> %s, type(%s)" % (option, str(value), type(value)), CONFIG_LOG_THRESHOLD)
        if option in GENERAL_OPTIONS_LIST:
            self._config_map[option] = value
        else:
            logger.debug("   (%s, %d)" % (kwargs['picture_type'], int(kwargs['cam_index'])), CONFIG_LOG_THRESHOLD)
            self._set_picture_option(option, value, kwargs['picture_type'], int(kwargs['cam_index']))

    def _set_picture_option(self, option, value, picture_type, cam_index):
        pic_type_attr = getattr(self._config_map[cam_index], picture_type)
        setattr(pic_type_attr, option, value)
        logger.debug("Pic Config after set: %s" % str(self._get_picture_option(option, picture_type, cam_index)), CONFIG_LOG_THRESHOLD)

    def get(self, option, **kwargs):
        """
        If processing a picture option, the following keyword parameter must be set:
            'picture_type': either PARAM_PICTURE_TYPE_TEMP or PARAM_PICTURE_TYPE_BACKUP
            'cam_index': camera index for which to modify the option
        """
        if option != OPTION_CURRENT_MONTH_DATA_USAGE_KB:
            logger.debug("Config.get:", CONFIG_LOG_THRESHOLD)
        if option in GENERAL_OPTIONS_LIST:
            v = self._config_map[option]
        else:
            v = self._get_picture_option(option, kwargs['picture_type'], int(kwargs['cam_index']))
        if option != OPTION_CURRENT_MONTH_DATA_USAGE_KB:
            logger.debug("   %s -> %s" % (option, str(v)), CONFIG_LOG_THRESHOLD)
        return v

    # noinspection PyMethodMayBeStatic
    def _get_picture_option(self, option, picture_type, cam_index):
        pic_type_attr = getattr(self._config_map[cam_index], picture_type)
        return getattr(pic_type_attr, option)

    def _format_option_for_output(self, opt, pic_type, cam_index):
        """
        Options may consist of complex object, as is the case for time related ones.
        In those cases, convert to proper string the requested object related option.
        """

        # Get object related option
        v = self.get(opt, picture_type=pic_type, cam_index=cam_index)
        try:
            v1 = self.get(opt, picture_type=pic_type, cam_index=cam_index + 1)
        except KeyError:
            v1 = None

        # if it's a datetime/time object, convert appropriately
        if opt in [OPTION_PICTURE_UPLOAD_START_TIME, OPTION_PICTURE_UPLOAD_STOP_TIME]:
            v = v.strftime(TIME_HM_FORMAT)
            if v1 is not None:
                v1 = v1.strftime(TIME_HM_FORMAT)
        elif opt == OPTION_PICTURE_UPLOAD_INTERVAL_TIME_DELTA:
            v = v.strftime(TIME_MS_FORMAT)
            if v1 is not None:
                v1 = v1.strftime(TIME_MS_FORMAT)
        return v, v1

    def __str__(self):
        config_str = "----------------------------------------\n"
        config_str += "%-30s %s GB\n" % ("Monthly data allowance:", self.get(OPTION_MONTHLY_DATA_ALLOWANCE_GB))
        config_str += "%-30s %d MB\n" % \
                      ("Current month data usage:", int(int(self.get(OPTION_CURRENT_MONTH_DATA_USAGE_KB)) / 1024))
        config_str += "%-30s %s MB\n" % ("Data cap upload stop margin:", self.get(OPTION_UPLOAD_STOP_MARGIN_MB))
        config_str += "%-30s %s\n" % ("Day of month data cap reset:", self.get(OPTION_DAY_OF_MONTH_DATA_CAP_RESET))
        config_str += "%-30s %s\n" % ("Date of last data cap reset:", str(self.get(OPTION_LAST_DATA_CAP_RESET_DATE)))
        config_str += "%-30s %s (s)\n" % ("FFMPEG timeout:", self.get(OPTION_FFMPEG_TIMEOUT))
        for pic_type in [PARAM_PICTURE_TYPE_TEMP, PARAM_PICTURE_TYPE_BACKUP]:
            config_str += "\n   ########################################\n"
            config_str += "   %-20s %s\n" % ("Picture type:", pic_type)
            config_str += "   ########################################\n\n"
            for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1, 2):
                if i < DEFAULT_NUMBER_OF_CAMERAS:
                    config_str += "   %-49s     %s\n" % ("=" * 49, "=" * 49)
                else:
                    config_str += "   %s\n" % ("=" * 49)
                for opt in PICTURE_OPTION_LIST:
                    if opt == OPTION_PICTURE_EXPIRY_TIME_DELTA and pic_type == PARAM_PICTURE_TYPE_TEMP:
                        continue

                    v, v1 = self._format_option_for_output(opt, pic_type, i)

                    if i < DEFAULT_NUMBER_OF_CAMERAS:
                        config_str += "   %-20s: %-30s  |  %-20s: %s\n" % (opt, v,
                                                                           opt, v1)
                    else:
                        config_str += "   %-20s: %s\n" % (opt, self.get(opt, picture_type=pic_type, cam_index=i))

        return config_str


def main():
    config = Config()
    for pic_type in [PARAM_PICTURE_TYPE_TEMP, PARAM_PICTURE_TYPE_BACKUP]:
        for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            config.set(OPTION_PICTURE_RESOLUTION, RES_640x480, picture_type=pic_type, cam_index=i)
            config.set(OPTION_PICTURE_EXPIRY_TIME_DELTA, datetime.timedelta(days=5), picture_type=pic_type, cam_index=i)
    print(str(config))

    config.write()
    config.read()

    for pic_type in [PARAM_PICTURE_TYPE_TEMP, PARAM_PICTURE_TYPE_BACKUP]:
        for i in range(1, DEFAULT_NUMBER_OF_CAMERAS + 1):
            config.set(OPTION_PICTURE_RESOLUTION, RES_1600x1200, picture_type=pic_type, cam_index=i)

    print(str(config))
    input("Close window or press enter to exit")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        watch_out_lib.MyLogger.MyLogger.set_default_class_level(2)

    main()
