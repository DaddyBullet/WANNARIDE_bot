# !/usr/bin/python3
# -*- coding: utf-8 -*- #

import pickle
from datetime import datetime, timedelta
from telepot.namedtuple import KeyboardButton, ReplyKeyboardMarkup

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Interval, ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

from json import loads, dumps
from geopy import Point

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, unique=True, nullable=False)
    user_name = Column(String, unique=True)
    start_time = Column(DateTime)
    exp_time = Column(Interval)
    location = Column(String)
    radius = Column(String)
    save_location = Column(Boolean, default=False)
    last_request = Column(DateTime)
    prev_command = Column(String)

    status_id = Column(Integer, ForeignKey('status.id'))
    ride_id = Column(Integer, ForeignKey('ride_type.id'))

    ride = relationship("RideType", back_populates="users")
    status = relationship("Status", back_populates="users")


class RideType(Base):
    __tablename__ = 'ride_type'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="ride")


class Status(Base):
    __tablename__ = 'status'

    id = Column(Integer, primary_key=True, autoincrement=True)
    status_name = Column(String, unique=True, nullable=False)
    users = relationship("User", back_populates="status")


def make_db():
    eng = create_engine('sqlite:///super_secure_users.db', echo=True)
    Base.metadata.create_all(eng)
    s = sessionmaker(bind=eng)()
    s.add_all([
        RideType(name="fix"),
        RideType(name="bicycle"),
        RideType(name="bmx"),
        RideType(name="roller blades"),
        RideType(name="skate"),
        RideType(name="longboard"),
        Status(status_name="Active"),
        Status(status_name="Subactive"),
        Status(status_name="Inactive"),
    ])
    s.commit()


def connect_to_db():
    eng = create_engine('sqlite:///super_secure_users.db', echo=True)
    return sessionmaker(bind=eng)


class Wonnarider(object):
    def __init__(self, s: Session, chat_id=None, uid=None, db_instance=None):
        if db_instance:
            db_instance.last_request = datetime.now()
            s.commit()
            self.db_instance = db_instance
            self._s = s
            self.chat_id = db_instance.chat_id
            self.uid = db_instance.user_name
            if not db_instance.ride:
                self.ride_type = None
            else:
                self.ride_type = db_instance.ride.name
            self.start_time = db_instance.start_time
            self.exp_time = db_instance.exp_time
            if not db_instance.location:
                self.location = None
            else:
                self.location = Point(**loads(db_instance.location))
            self.radius = float(db_instance.radius) if db_instance.radius else None
            self.save_location = db_instance.save_location
            self.prev_command = db_instance.prev_command
            self.last_request = db_instance.last_request
            return

        u = s.query(User).filter(User.chat_id == chat_id).one_or_none()
        if not u:
            u = User(chat_id=chat_id, user_name=uid, last_request=datetime.now(), status_id=2)
            s.add(u)
        s.commit()

        self.db_instance = u
        self._s = s
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
        self.db_instance.start_time = datetime.now()
        self._s.commit()
        self.start_time = datetime.now()

    def tagName(self):
        if self.db_instance.user_name:
            return '@' + self.db_instance.user_name
        if self.uid:
            return '@'+self.uid
        # else:
        #     return str(self.chat_id)

    def quitQueueKeyboard(self):
        # self.start_time = None
        return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/stop_searching')]])

    def quitQueue(self):
        self.db_instance.start_time = None
        self._s.commit()
        self.start_time = None
        if not self.save_location:
            self.setLocation(None)

    def setRideType(self, rt):
        self.db_instance.ride = self._s.query(RideType).filter(RideType.name == rt).first()
        self._s.commit()

        self.ride_type = rt

    def setLocation(self, l):
        self.db_instance.location = l
        self._s.commit()
        if not l:
            self.location = None
        else:
            self.location = Point(**loads(l))

    def setSaveLoc(self, issave):
        self.db_instance.save_location = issave
        self._s.commit()
        self.save_location = issave

    def setRadius(self, r):
        self.db_instance.radius = str(r)
        self._s.commit()
        self.radius = float(r)

    def setExpTime(self, h, m=0):
        self.db_instance.exp_time = timedelta(hours=h, minutes=m)
        self._s.commit()
        self.exp_time = timedelta(hours=h, minutes=m)

    def reenterQueue(self):
        self.startSearch()

    def setPrevCommand(self, cm):
        self.db_instance.prev_command = cm
        self._s.commit()
        self.prev_command = cm

    def refreshLastRequestTime(self):
        self.db_instance.last_request = datetime.now()
        self._s.commit()
        self.last_request = datetime.now()

    def isActive(self):
        if not self.start_time:
            return False
        return datetime.now() < self.db_instance.start_time + self.db_instance.exp_time
        # return datetime.now() < self.start_time + self.exp_time

    def unsettedParams(self):
        keys = []
        if not self.ride_type:
            keys.append([KeyboardButton(text='/set_category')])
        if not self.radius:
            keys.append([KeyboardButton(text='/set_radius')])
        if not self.exp_time:
            keys.append([KeyboardButton(text='/set_waiting_time')])
        if not keys:
            if not self.isActive():
                # users = pickle.load(open('users.pickle', 'r+b'))
                # for u in users:
                #     if u.chat_id == self.chat_id:
                #         users.remove(u)
                # users.append(self)
                # with open('users.pickle', 'w+b') as f:
                #     pickle.dump(users, f)
                # del users
                return ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='/wonnaride')]])
            else:
                return self.quitQueueKeyboard()
        return ReplyKeyboardMarkup(keyboard=keys)

    def about(self):
        retstr = ''
        retstr += 'Username: ' + ('None' if not self.uid else self.uid)
        retstr += '\nRide type: ' + ('None' if not self.ride_type else self.ride_type) + ' /set_category'
        retstr += '\nRadius: ' + ('None' if not self.radius else str(self.radius)) + ' /set_radius'
        # retstr += '\nTime in queue: ' + str(int(self.exp_time.seconds/3600)) + ':'\
        #           + str(int((self.exp_time.seconds%3600)/60))
        retstr += '\nTime in queue: ' + ('None' if not self.exp_time else str(self.exp_time)) + ' /set_waiting_time'
        retstr += '\nLocation: ' + ('None' if not self.location else str(self.location))
        retstr += '\nSave location? ' + ('Yes' if self.save_location else 'No') + ' /save_location'

        return retstr

