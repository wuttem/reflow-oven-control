#!/usr/bin/python
# coding: utf8

import time
import serial
import struct
import logging

from threading import Thread
from simple_hdlc import HDLC


class Oven(object):
    def __init__(self, serial_url):
        self.serial = serial.serial_for_url(serial_url, baudrate=115200)
        self.hdlc = HDLC(self.serial)

        self.t = None
        self.running = False

        self.temp_case = None
        self.temp_l = None
        self.temp_r = None
        self.power = None

    def start(self):
        self.hdlc.startReader(self.frame_callback)
        if self.t is None:
            self.running = True
            self.t = Thread(target=self._run)
            self.t.daemon = True
            self.t.start()

    def stop(self):
        self.hdlc.stopReader()
        self.running = False
        self.t.join()
        self.t = None

    def getStatus(self):
        status_frame = struct.pack("<HB", 0, 0)
        self.hdlc.sendFrame(status_frame)

    def setControl(self, hf, heat, fan):
        cmd_frame = struct.pack("<HBBBB", 0, 1, int(hf), int(heat), int(fan))
        self.hdlc.sendFrame(cmd_frame)

    def playTone(self, freq, duration):
        tone_frame = struct.pack("<HBBB", 0, 2, int(freq/10), int(duration*100))
        self.hdlc.sendFrame(tone_frame)

    def getTemp(self):
        if self.temp_l and self.temp_r:
            return (self.temp_l + self.temp_r) / 2
        return None

    def _run(self):
        while self.running:
            # Get Status
            self.getStatus()
            time.sleep(0.70)

    def __str__(self):
        return "Power: {}, Case: {}, Left: {}, Right: {}".format(
            self.power, self.temp_case, self.temp_l, self.temp_r)

    def frame_callback(self, data):
        # Data Paket
        if len(data) >= 10:
            power = struct.unpack("<B", data[2])[0]
            temp_case = struct.unpack("<H", data[4:6])[0]
            temp_r = struct.unpack("<H", data[6:8])[0]
            temp_l = struct.unpack("<H", data[8:10])[0]
            self.power = bool(power)
            self.temp_case = float(temp_case) / 10
            self.temp_l = float(temp_l) / 10 + self.temp_case
            self.temp_r = float(temp_r) / 10 + self.temp_case
        else:
            pass

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)
    o = Oven("/dev/ttyUSB0")
    o.start()
    while 1:
        time.sleep(2.0)
        print str(o)
    o.stop()
