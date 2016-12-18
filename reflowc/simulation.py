#!/usr/bin/python
# coding: utf8

import time
from threading import Thread
from random import random
from random import randint


class OvenSimulator(object):
    def __init__(self, start_temp=25.0):
        self.temp = start_temp
        self.timer = 0.0
        self.heat = False
        self.fan = False
        self.running = False
        self.t = None
        self.fan_power = 1.0
        self.heat_power = 1.0

    def getTemp(self):
        return self.temp

    def setHeater(self, on, power=100):
        self.heat = bool(on)
        self.heat_power = float(power) / 100.0

    def setFan(self, on, power=100):
        self.fan = bool(on)
        self.fan_power = float(power) / 100.0

    def getStatus(self):
        return {"heat": self.heat, "fan": self.fan}

    def start(self):
        if self.t is None:
            self.running = True
            self.t = Thread(target=self._run)
            self.t.daemon = True
            self.t.start()

    def stop(self):
        self.running = False
        self.t.join()
        self.t = None

    def _run(self):
        heat = self.heat
        fan = self.fan

        while self.running:
            x = self.temp
            if heat:
                x += random() * (3.0 * self.heat_power) + 1.0
            elif x >= 20.0:
                x -= random() * (x / 50)
            if fan and x >= 25:
                x -= random() * (5.0 * self.fan_power)
            self.temp = x
            self.timer += 0.99
            if randint(0, 4) < 2:
                heat = self.heat
                fan = self.fan
            time.sleep(0.99)
