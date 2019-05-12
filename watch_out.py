"""
Notes
    Pixel formats size per pixel
      yuv410p:   9 bits/pixel     worst quality
      yuvj420p: 12 bits/pixel     second best quality
      yuv420p:  12 bits/pixel     second best quality
      yuv422p:  16 bits/pixel     best quality
"""

# TODO: UI/command line option for config file

from watch_out_lib.Config import *
from watch_out_lib.MyLogger import logger, get_trace
from watch_out_lib.DataCapHandler import DataCapHandler
from watch_out_lib.WatchOutSettings import WatchOutSettings
from watch_out_lib.PictureHandler import PictureHandler
from watch_out_lib.TimeTracker import time_tracker

import argparse
import signal
import sys
import time

EXCEPTION_SLEEP_TIME = 20


def signal_handler(sig, frame):
    if sig == signal.SIGINT:
        print('Exiting (<ctrl-c> pressed)')
        sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


class WatchOut:
    def __init__(self, args):
        logger.debug('##############################', 0)
        logger.debug('RUN START', 0)
        logger.debug('##############################', 0)
        self._config = Config()
        self._settings = WatchOutSettings(args.camera_password)
        if args.simulation is not None:
            time_tracker.set_time_multiplier(int(args.simulation[1]))

        self._data_cap_handler = DataCapHandler(args, self._config)
        self._picture_handler = PictureHandler(args, self._config, self._data_cap_handler)

        self._single_instance_lock = None
        self._set_single_instance_running()

    def run(self):
        while True:
            try:
                time_tracker.tick_tock()
                self._config.read()
                self._data_cap_handler.check_data_cap()
                self._picture_handler.run()
            except Exception as e:
                msg = get_trace(e)
                logger.warning(msg)
                time.sleep(EXCEPTION_SLEEP_TIME)

            time.sleep(1)

    def _set_single_instance_running(self):
        """
        We lock a file to make sure only one process
        can run. If multiple processes are spawn,
        they will all fail except the first one.
        Lock is released upon termination.
        """
        if sys.platform == 'linux':
            import fcntl
            lock_file = Path("/tmp/.watch_out_file_lock")
            self._single_instance_lock = open(str(lock_file), 'w')
            fcntl.flock(self._single_instance_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        elif sys.platform == 'win32':
            import msvcrt
            lock_file = Path("%s/.watch_out_file_lock" % os.environ['USERPROFILE'])
            self._single_instance_lock = open(str(lock_file), 'w')
            msvcrt.locking(self._single_instance_lock.fileno(), msvcrt.LK_RLCK, 4096)
        else:
            raise Exception("%s platform not supported" % sys.platform)


def parse_args():
    parser = argparse.ArgumentParser(description='watch_out! Camera Picture Uploader Program')

    parser.add_argument('camera_password',
                        help='Camera password')

    parser.add_argument('-f',
                        dest='debug_output_file',
                        default="",
                        action='store',
                        help='Output debugging chatter to specified output file')

    parser.add_argument('-v',
                        dest='verbosity',
                        default=0,
                        action='count',
                        help='Debug chatter. Use multiple times to increase verbosity')

    parser.add_argument('-s',
                        dest='simulation',
                        metavar=("DATA_CAP_MG", "TIME_MULTIPLIER"),
                        default=[None, 1],
                        nargs=2,
                        help='For debugging purposes, set the data cap in MB and a passing time multiplier '
                             '(max 7200, 2 hours per second).')

    args = parser.parse_args()

    if args.simulation is not None and int(args.simulation[1]) > 7200:
        args.simulation[1] = 7200

    args.epilog = """NOTES

If no password are necessary, specify "".
"""

    return args


def main():
    args = parse_args()

    if args.debug_output_file != "":
        logger.set_output_file(args.debug_output_file)

    logger.set_default_class_level(args.verbosity)

    d = WatchOut(args)
    d.run()


if __name__ == "__main__":
    main()
