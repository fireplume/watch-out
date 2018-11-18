import logging
from logging.handlers import RotatingFileHandler
import sys
import traceback

# DEBUG LEVEL BY DEFAULT
DEFAULT_DEBUG_LEVEL = logging.DEBUG


def get_trace(an_exception):
    s = traceback.extract_tb(sys.exc_info()[2])
    st = traceback.format_list(s)
    msg = "".join(st + [str(an_exception)])
    return msg


class MyLogger:
    logger = None
    debug_level_threshold = 0

    def __init__(self):
        if self.logger is not None:
            raise Exception('Only one instance of MyLogger allowed')
        self.logger = logging.getLogger("Console")
        self.logger.setLevel(DEFAULT_DEBUG_LEVEL)
        self._handler = logging.StreamHandler()
        self._handler.setLevel(DEFAULT_DEBUG_LEVEL)
        self._formatter = logging.Formatter(fmt="{name:s} {levelname:8s} {message}", style='{')
        self._handler.setFormatter(self._formatter)
        self.logger.addHandler(self._handler)

    @classmethod
    def set_default_class_level(cls, level):
        MyLogger.debug_level_threshold = level

    def warning(self, msg, level=1):
        if level <= MyLogger.debug_level_threshold:
            self.logger.warning(msg)
            self._handler.flush()

    def debug(self, msg, level=1):
        if level <= MyLogger.debug_level_threshold:
            self.logger.debug(msg)
            self._handler.flush()

    def error(self, msg):
        self.logger.error(msg)
        self._handler.flush()

    def set_output_file(self, output_file):
        self.logger.removeHandler(self._handler)
        self._handler = RotatingFileHandler(output_file,
                                            mode='a',
                                            maxBytes=1024 * 1024,
                                            backupCount=2)
        self._handler.setFormatter(self._formatter)
        self.logger.addHandler(self._handler)


if MyLogger.logger is None:
    MyLogger.logger = MyLogger()
logger = MyLogger.logger

if __name__ == "__main__":
    # For debugging
    logger.warning("Level 1 warning should not appear by default!")
    logger.debug("Level 1 debug should not appear by default!")

    logger.set_default_class_level(1)

    logger.warning("Level 1 warning should now appear", 1)
    logger.debug("Level 1 debug should now appear", 1)

    logger.set_output_file("watch_out.log")

    logger.set_default_class_level(4)

    logger.warning("Level 3 warning should appear when level threshold is 4!", 3)
    logger.debug("Level 3 debug should appear when level threshold is 4!", 3)

    logger.warning("Level 5 warning should not appear when level threshold is 4", 5)
    logger.debug("Level 5 debug should not now appear when level threshold is 4", 5)
