# !/usr/bin/python3
# -*- coding: utf-8 -*- #

from datetime import datetime, timedelta, time
class Wonnarider(object):
    def __init__(self, chat_id, uid=None):
        self.chat_id = chat_id
        self.uid = uid
        self.ride_type = 'bicycle'
        self.start_time = None
        self.exp_time = timedelta(hours=1)
        self.location = None
        self.radius = 20
        self.prev_command = None

    def startSearch(self):
        self.start_time = datetime.now()

    def tagName(self):
        if self.uid:
            return '@'+self.uid
        else:
            return str(self.chat_id)

    def quitQueue(self):
        pass

    def setRideType(self, rt):
        self.ride_type = rt

    def setLocation(self, l):
        self.location = l

    def setRadius(self, r):
        self.radius = r

    def setExpTime(self):
        pass

    def reenterQueue(self):
        self.startSearch()