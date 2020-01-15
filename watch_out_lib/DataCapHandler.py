from watch_out_lib.Config import *
from watch_out_lib.MyLogger import logger
from watch_out_lib.TimeTracker import time_tracker


class DataCapHandler:
    def __init__(self, args, config):
        self._config = config
        self._simulation = args.simulation
        if self._simulation is None or self._simulation[0] is None:
            self._data_cap_kb = int(self._config.get(OPTION_MONTHLY_DATA_ALLOWANCE_GB)) * 1024 * 1024
        else:
            self._data_cap_kb = int(args.simulation[0]) * 1024

        self._current_data_usage_bytes = None
        self._upload_stop_margin_bytes = None
        self._data_cap_reached = None

        self._check_config()

    def add_usage(self, bytes_used):
        self._current_data_usage_bytes += bytes_used
        logger.debug("   Current data usage: %d KB" % (self._current_data_usage_bytes / 1024))
        self._config.write(OPTION_CURRENT_MONTH_DATA_USAGE_KB, int(self._current_data_usage_bytes / 1024))

    def check_data_cap(self):
        if self._simulation is None:
            self._data_cap_kb = int(self._config.get(OPTION_MONTHLY_DATA_ALLOWANCE_GB)) * 1024 * 1024

        self._check_data_cap_reset()

        if self._data_cap_reached:
            self._check_config()

        self._data_cap_reached = (self._current_data_usage_bytes + self._upload_stop_margin_bytes) >= (self._data_cap_kb * 1024)

    def _check_config(self):
        self._current_data_usage_bytes = int(self._config.get(OPTION_CURRENT_MONTH_DATA_USAGE_KB)) * 1024
        self._upload_stop_margin_bytes = int(self._config.get(OPTION_UPLOAD_STOP_MARGIN_MB)) * 1024 * 1024

    def data_cap_reached(self):
        return self._data_cap_reached

    def _check_data_cap_reset(self):
        # check for monthly data cap reset
        # Note that we can't rely on the day of the month reset date only as not
        # all months have the same number of days.
        monthly_reset_day = int(self._config.get(OPTION_DAY_OF_MONTH_DATA_CAP_RESET))
        current_day = time_tracker.current_time.day
        current_month = time_tracker.current_time.month
        last_reset_date = self._config.get(OPTION_LAST_DATA_CAP_RESET_DATE)
        last_reset_month = last_reset_date.month

        #######################
        # Data cap reset cases
        #######################

        current_month_reset = self._config.get(OPTION_CURRENT_MONTH_RESET)

        if current_month_reset:
            if time_tracker.current_time.day > monthly_reset_day:
                logger.debug("Resetting current month reset flag (==False)", 1)
                self._config.write(OPTION_CURRENT_MONTH_RESET, False)
            else:
                # We've already reset today
                return

        # Data Cap Reset Day
        data_cap_reset_case_1 = (monthly_reset_day == current_day) and not current_month_reset

        # Month ends before reset day is reached, reset on the 1st
        data_cap_reset_case_2 = (current_month != last_reset_month) and \
                                (current_day == 1) and \
                                (monthly_reset_day >= 28)

        # It's been more than one month since we reset
        data_cap_reset_case_3 = (time_tracker.current_time - last_reset_date).days >= 31

        if data_cap_reset_case_1 or \
                data_cap_reset_case_2 or \
                data_cap_reset_case_3:
            logger.debug("*******************************")
            logger.debug("Monthly data cap reset %s" % str(time_tracker.current_time), 1)
            logger.debug("Setting current month reset flag (==True)", 1)
            logger.debug("*******************************")
            # New billing month, reset data counter, update last data reset date
            self._config.write(OPTION_CURRENT_MONTH_RESET, True)
            self._config.write(OPTION_LAST_DATA_CAP_RESET_DATE, time_tracker.current_time)
            self._config.write(OPTION_CURRENT_MONTH_DATA_USAGE_KB, 0)
            self._config.read()
            self._current_data_usage_bytes = 0
            self._data_cap_reached = False

    def update_config_data_usage(self):
        self._config.write(OPTION_CURRENT_MONTH_DATA_USAGE_KB, int(self._current_data_usage_bytes / 1024))
