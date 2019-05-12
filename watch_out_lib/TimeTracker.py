from watch_out_lib.MyLogger import logger

from datetime import datetime, timedelta
from math import floor


class TimeTracker:
    time_tracker = None

    def __init__(self):
        if self.time_tracker is not None:
            raise Exception("Only one instance of TimeTracker allowed")
        self._time_multiplier = 1
        self._last_tick_tock = datetime.today()
        self._init_time = datetime.today()
        self._day_changed = False
        self._hour_changed = False
        self._day_or_hour_changed = False

    def set_time_multiplier(self, multiplier):
        self._time_multiplier = multiplier

    def is_time_simulated(self):
        return self._time_multiplier != 1

    def _get_elapsed_time(self):
        real_elapsed_time = datetime.today() - self._init_time

        # Can't set timedelta with seconds >= 24*3600 seconds, break down into days, hours, seconds:
        accelerated_time_elapsed_total_seconds = real_elapsed_time.total_seconds() * self._time_multiplier
        days_elapsed = floor(float(accelerated_time_elapsed_total_seconds) / (24 * 3600))
        hours_elapsed = floor(float(accelerated_time_elapsed_total_seconds - days_elapsed * 24 * 3600) / 3600)
        remaining_seconds = accelerated_time_elapsed_total_seconds - (days_elapsed * 3600 * 24) - (hours_elapsed * 3600)

        return timedelta(days=days_elapsed, hours=hours_elapsed, seconds=remaining_seconds)

    def tick_tock(self):
        current_time = self._init_time + self._get_elapsed_time()

        self._day_changed = self._last_tick_tock.day != current_time.day
        self._hour_changed = self._last_tick_tock.hour != current_time.hour

        self._day_or_hour_changed = False
        if self._day_changed or self._hour_changed:
            self._day_or_hour_changed = True
            logger.debug("New current time:   %s" % current_time.strftime("Month: %m   Day: %d   Hour: %H"))

        self._last_tick_tock = current_time

    def day_or_hour_changed(self):
        return self._day_or_hour_changed

    def hour_changed(self):
        return self._hour_changed

    @property
    def current_time(self):
        return self._last_tick_tock


if TimeTracker.time_tracker is None:
    TimeTracker.time_tracker = TimeTracker()
time_tracker = TimeTracker.time_tracker
