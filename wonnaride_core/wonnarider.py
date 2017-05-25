# !/usr/bin/python3
# -*- coding: utf-8 -*- #

from datetime import datetime, timedelta
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup

class Wonnarider(object):
    def __init__(self, chat_id, uid=None):
        self.chat_id = chat_id
        self.uid = uid
        self.ride_type = None
        self.start_time = None
        self.exp_time = None
        self.location = None
        self.radius = None
        self.save_location = False
        self.prev_command = None
        self.last_request = datetime.now()

    def startSearch(self):
        self.start_time = datetime.now()

    def tagName(self):
        if self.uid:
            return '@'+self.uid
        # else:
        #     return str(self.chat_id)

    def quitQueueKeyboard(self):
        # self.start_time = None
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/stop_searching')]])

    def quitQueue(self):
        self.start_time = None

    def setRideType(self, rt):
        self.ride_type = rt

    def setLocation(self, l):
        self.location = l

    def setRadius(self, r):
        self.radius = r

    def setExpTime(self, h, m=0):
        self.exp_time = timedelta(hours=h, minutes=m)

    def reenterQueue(self):
        self.startSearch()

    def setPrevCommand(self, cm):
        self.prev_command = cm

    def refreshLastRequestTime(self):
        self.last_request = datetime.now()

    def isActive(self):
        return datetime.now() < self.start_time + self.exp_time

    def unsettedParams(self):
        keys = []
        if not self.ride_type:
            keys.append([KeyboardButton(text='/set_category')])
        if not self.radius:
            keys.append([KeyboardButton(text='/set_radius')])
        if not self.exp_time:
            keys.append([KeyboardButton(text='/set_waiting_time')])
        if not keys:
            return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/wonnaride')]])
        return ReplyKeyboardMarkup(keyboard=keys)

    def about(self):
        retstr = ''
        retstr += 'Username: ' + ('None' if not self.uid else self.uid)
        retstr += '\nRide type: ' + ('None' if not self.ride_type else self.ride_type)
        retstr += '\nRadius: ' + ('None' if not self.radius else str(self.radius))
        # retstr += '\nTime in queue: ' + str(int(self.exp_time.seconds/3600)) + ':'\
        #           + str(int((self.exp_time.seconds%3600)/60))
        retstr += '\nTime in queue: ' + ('None' if not self.exp_time else str(self.exp_time))
        retstr += '\nLocation: ' + ('None' if not self.location else str(self.location))
        return retstr

