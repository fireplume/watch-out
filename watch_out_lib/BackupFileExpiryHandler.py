from watch_out_lib.MyLogger import logger
from watch_out_lib.TimeTracker import time_tracker

import datetime
import os
import re
import shutil
import stat
from pathlib import Path


class AddChildError(Exception):
    pass


class FileExpiryHandler:
    ROOT_FOLDER = 0
    DATE_FOLDER = ROOT_FOLDER + 1
    HOUR_FOLDER = DATE_FOLDER + 1
    PICTURES = HOUR_FOLDER + 1

    _file_type = [ROOT_FOLDER,
                  DATE_FOLDER,
                  HOUR_FOLDER,
                  PICTURES]

    _longest_expiry_delta = None

    def __init__(self,
                 path: Path,
                 parent=None,
                 level=ROOT_FOLDER):
        self._path = path
        self._level = level
        self._parent = parent

        self._children = {}
        self._expiry = None
        self._creation_time = None
        self._longest_expiry_delta = None

        # Backup picture storage folder path structure is:
        # self.backup_pictures_root_path/<YYYY-mm-dd>/<hour>h/
        # These are datetime compatible format string
        self._backup_folder_date_format = "%Y-%m-%d"
        self._folder_ymd_re = re.compile(r"(\d{4})-(\d{2})-(\d{2})\s*$")
        self._backup_folder_time_format = "%Hh"
        self._folder_h_re = re.compile(r"(\d{2})h\s*$")
        self._time_ms_format = "%Mm%Ss"
        self._picture_ms_format_re = re.compile(r"(\d{2})m(\d{2})s\.")

        self._picture_element_re = re.compile(r"^(((.*?\d{4}-\d{2}-\d{2})\S\d{2}h)\S\S+)")

    @property
    def backup_folder_date_format(self):
        return self._backup_folder_date_format

    @property
    def backup_folder_time_format(self):
        return self._backup_folder_time_format

    @property
    def time_ms_format(self):
        return self._time_ms_format

    def process_expiry(self):
        destroy_set = []
        for child in self.iter_children_recursive():
            if child.is_expired() or \
                    not child.contain_pictures():
                destroy_set.append(child)

        for child in destroy_set:
            child.destroy()

        if self.is_empty():
            logger.debug("Backup picture expiry: none left!", 1)

    @classmethod
    def set_longest_expiry_delta(cls, delta: datetime.timedelta):
        cls._longest_expiry_delta = delta

    def add_child(self, child_file: Path, level, real_delta=None):
        # Already exists?
        if self.exists(child_file):
            return

        use_delta = FileExpiryHandler._longest_expiry_delta
        if real_delta is not None:
            use_delta = real_delta

        child_handler = FileExpiryHandler(child_file, self, level)
        child_handler.set_creation_time()
        child_creation_time = child_handler.get_creation_time()
        if child_creation_time is None:
            child_handler.destroy()
            raise AddChildError()
        child_handler._set_expiry(child_creation_time + use_delta)
        self._children[str(child_file)] = child_handler
        return child_handler

    def add_picture(self, output_file, expiry_delta: datetime.timedelta):
        m = self._picture_element_re.search(output_file)
        if m:
            date_path = Path(m.group(3))
            hour_path = Path(m.group(2))
            pic_path = Path(m.group(1))

            try:
                date_child = self.get_child(date_path)
                date_child.set_creation_time()
            except:
                raise AddChildError("Unable to add picture %s (date child None?)" % str(output_file))

            try:
                hour_child = date_child.get_child(hour_path)
                hour_child.set_creation_time()
                hour_child.add_child(pic_path,
                                     level=FileExpiryHandler.PICTURES,
                                     real_delta=expiry_delta)
            except:
                raise AddChildError("Unable to add picture %s (hour child None?)" % str(output_file))
        else:
            raise AddChildError("Unable to add picture %s" % str(output_file))

    def exists(self, child_path: Path):
        if str(child_path) in self._children:
            return True
        return False

    def get_child(self, child_path: Path):
        if str(child_path) in self._children:
            return self._children[str(child_path)]
        else:
            logger.warning("get_child: unknown child: %s" % str(child_path))
            return None

    def remove_child(self, child):
        if str(child) in self._children:
            del self._children[str(child)]
        else:
            logger.warning("remove_child: unknown child: %s" % str(child))

    def get_creation_time(self):
        return self._creation_time

    def set_creation_time(self):
        self._creation_time = self.get_file_creation_time(self._path, self._parent.get_creation_time())

    def is_expired(self):
        if self._expiry is not None:
            return time_tracker.current_time > self._expiry
        return self.is_empty() or not self.contain_pictures()

    @property
    def level(self):
        return self._level

    def _set_expiry(self, expiry_date: datetime.datetime):
        self._expiry = expiry_date

    def is_empty(self):
        if len(self._children) == 0:
            return True
        return False

    def contain_pictures(self):
        if self.level == FileExpiryHandler.PICTURES:
            return True

        pic_flag = False
        for child in self.iter_children_recursive():
            if child.level == FileExpiryHandler.PICTURES:
                pic_flag = True
                break
        return pic_flag

    def iter_children_recursive(self):
        """
        Yields all children bottom up
        :return:
        """
        for child in self._children:
            if not self._children[str(child)].is_empty():
                for sub_child in self._children[str(child)].iter_children_recursive():
                    yield sub_child
            else:
                yield self._children[str(child)]

    @staticmethod
    def _delete_folder_recursive(folder):
        os.chmod(folder, stat.S_IWRITE)
        for root, dirs, files in os.walk(str(folder)):
            for d in dirs:
                del_dir = os.path.join(root, d)
                logger.debug("   Allow deletion for %s" % del_dir)
                os.chmod(del_dir, stat.S_IWRITE)
        shutil.rmtree(str(folder))

    def get_file_creation_time(self, file_path, parent_creation_date=None):
        if not time_tracker.is_time_simulated():
            return datetime.datetime.fromtimestamp(os.path.getctime(file_path))

        m = self._folder_ymd_re.search(str(file_path))
        if m:
            return datetime.datetime(year=int(m.group(1)),
                                     month=int(m.group(2)),
                                     day=int(m.group(3)))

        m = self._folder_h_re.search(str(file_path))
        if m and parent_creation_date is not None:
            return datetime.datetime(year=parent_creation_date.year,
                                     month=parent_creation_date.month,
                                     day=parent_creation_date.day,
                                     hour=int(m.group(1)))

        m = self._picture_ms_format_re.search(str(file_path))
        if m and parent_creation_date is not None:
            return datetime.datetime(year=parent_creation_date.year,
                                     month=parent_creation_date.month,
                                     day=parent_creation_date.day,
                                     hour=parent_creation_date.hour,
                                     minute=int(m.group(1)),
                                     second=int(m.group(2)))

        return None

    def set_children(self,
                     level=DATE_FOLDER):
        is_picture_level = level == FileExpiryHandler.PICTURES

        for child_file in self._path.glob("*"):
            if is_picture_level and not os.path.isfile(child_file):
                self._delete_folder_recursive(child_file)
            elif not is_picture_level and not os.path.isdir(child_file):
                os.remove(child_file)

            try:
                child_handler = self.add_child(child_file, level)
            except AddChildError:
                continue

            if not is_picture_level:
                child_handler.set_children(level=level + 1)

    def destroy(self):
        logger.debug("   Self destructing! %s" % str(self._path))
        logger.debug("      Expiry: %s" % str(self._expiry))
        logger.debug("      Empty: %s" % self.is_empty())
        if self._level == FileExpiryHandler.PICTURES and os.path.isfile(self._path):
            os.remove(self._path)
        else:
            self._delete_folder_recursive(self._path)
        self._parent.remove_child(self._path)

    def print_debug(self):
        buf = []
        buf.append("###########################################################")
        buf.append("### BACKUP FILES ###")
        buf.append("###########################################################")
        for child in self.iter_children_recursive():
            buf.append("----> %s" % str(child))
        if len(buf) > 3:
            for b in buf:
                logger.debug(b, 1)

    def __str__(self):
        return str(self._path)
