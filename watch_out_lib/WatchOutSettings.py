from pathlib import Path
import os
import sys


class WatchOutSettings:
    watch_out_settings = None

    def __init__(self, camera_password):
        if WatchOutSettings.watch_out_settings is not None:
            raise Exception("Only one instance of WatchOutSettings allowed")

        if sys.platform == 'linux':
            # /home/<user>
            self._user_path = Path(os.environ['HOME'])
            self.ffmpeg_binary_path = Path("/usr/local/bin/ffmpeg")
        elif sys.platform == 'win32':
            # c:/Users/<username>
            self._user_path = Path(os.environ['USERPROFILE'])
            self.ffmpeg_binary_path = Path("C:/App/ffmpeg/bin/ffmpeg.exe")
        else:
            raise Exception("%s platform not supported" % sys.platform)

        self.camera_password = camera_password

        # Corresponds to PARAM_PICTURE_TYPE_TEMP
        self.temp_pictures_path = self._user_path.joinpath("Google Drive/watch_out/temp")
        # Corresponds to PARAM_PICTURE_TYPE_BACKUP
        self.backup_pictures_root_path = self._user_path.joinpath("Google Drive/watch_out/backup")

        # When data cap is reached, this picture is copied over the self.temp_pictures_path
        # So people can see the data cap has been reached. You can put in that location
        # A warning picture such as a unhappy smiley pic or any such picture of your choice
        # It should be named 'data_cap_reached.jpg'
        self.data_cap_reached_picture_name = "data_cap_reached.jpg"
        self.data_cap_reached_picture_path = self._user_path.joinpath("Google Drive/watch_out", self.data_cap_reached_picture_name)

        # FFMPEG configuration
        # camera_url example: rtsp://admin:{password:s}@192.168.1.2:554/ch0{camera_index:d}/0
        self.ffmpeg_output_format = "jpg"
        # Format parameter:  camera_url(pre-formatted), protocol(udp|tcp)
        self.ffmpeg_base_command = "%s -y -rtsp_transport {protocol:s} -i {camera_url:s}" % self.ffmpeg_binary_path
        # Format parameters: (ffmpeg_base_command, quality, resolution, grayscale, pix_fmt, output_file(formatted with output format)
        self.ffmpeg_command_format_string = \
            "{ffmpeg_base_command:s} -frames:v 1 -q:v {quality:d} -vf scale={resolution:s}{grayscale:s} -pix_fmt {pix_fmt:s} -update 1 \"{output_file:s}\""

        self.exception_sleep_time = 60
        self.data_cap_reached_sleep_time = 15

        WatchOutSettings.watch_out_settings = self

    @classmethod
    def get_singleton(cls):
        return cls.watch_out_settings
