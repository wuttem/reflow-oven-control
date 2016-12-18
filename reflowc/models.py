#!/usr/bin/python
# coding: utf8

import datetime as dt
import numpy as np
import pandas as pd


INTERPOLATIONS = ["linear", "nearest", "quadratic", "cubic"]


class TempProfile(object):
    def __init__(self):
        self.start = dt.datetime(year=1970, month=1, day=1)
        self.updated = False
        #x = np.linspace(0, 5*60, 10)
        #y = pd.Series(np.sin(x))
        self._profile = None
        self.points = pd.Series()
        self.method = INTERPOLATIONS[0]
        #for i in range(len(x)):
        #    self.insertPoint(x[i], y[i])

    def setInterpolation(self, method):
        if method in INTERPOLATIONS:
            self.method = method
            self.updated = True
        else:
            raise ValueError("invalid interpolation method")

    @property
    def profile(self):
        if self._profile is None or self.updated:
            if len(self.points) > 3:
                self._profile = self.points.resample("1s", how="mean").interpolate(self.method)
            elif len(self.points > 1):
                self._profile = self.points.resample("1s", how="mean").interpolate("linear")
            else:
                self._profile = self.points
            self.updated = False
        return self._profile

    def getTarget(self, ts):
        idx = dt.timedelta(seconds=ts) + self.start
        if idx <= self.profile.index[0]:
            return self.profile[0]
        if idx >= self.profile.index[-1]:
            return self.profile[-1]
        i = self.profile.index.get_loc(idx, method="backfill", tolerance=dt.timedelta(seconds=5))
        return self.profile[i]

    @property
    def timestamps(self):
        return [int(t.value // 10 ** 9) for t in self.profile.index]

    @property
    def point_timestamps(self):
        return [int(t.value // 10 ** 9) for t in self.points.index]

    @property
    def values(self):
        return self.profile.tolist()

    @property
    def point_values(self):
        return self.points.tolist()

    def insertPoint(self, ts, value):
        new_ts = int(round(ts, -1))
        idx = dt.timedelta(seconds=new_ts) + self.start
        self.points.set_value(idx, value)
        self.points.drop_duplicates(inplace=True)
        self.updated = True


class PID(object):
    def __init__(self, kp=1, ki=1, kd=1):
        self.ki = ki
        self.kp = kp
        self.kd = kd
        self.lastNow = dt.datetime.now()
        self.iterm = 0
        self.lastErr = 0

    def update(self, setpoint, ispoint):
        now = dt.datetime.now()
        timeDelta = (now - self.lastNow).total_seconds()

        error = float(setpoint - ispoint)
        self.iterm += (error * timeDelta * self.ki)
        self.iterm = sorted([-1, self.iterm, 1])[1]
        dErr = (error - self.lastErr) / timeDelta

        output = self.kp * error + self.iterm + self.kd * dErr
        output = sorted([-100.0, output, 100.0])[1]
        self.lastErr = error
        self.lastNow = now

        return output