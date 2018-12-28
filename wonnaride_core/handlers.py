# !/usr/bin/python3
# -*- coding: utf-8 -*- #

import pickle
import os.path
from pprint import pprint
from geopy.distance import great_circle
from wonnaride_core.wonnarider import Wonnarider, Status, User

from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

active_wonnariders = []
semiacive_wonnariders = []
ride_types = ['bicycle', 'fix', 'bmx', 'roller blades', 'skate', 'longboard']
command_list = ['/wonnaride', '/settings', '/set_radius', '/set_category', '/set_waiting_time',
                '/stop_searching', '/save_location', '/help', '/test']
userspath = 'users.pickle'
val_err_msg = 'Please enter correct values'

init_msg = 'Hi! I want to help you to find some people near to spend your time with them.' \
           'You can choose the activity, how long can you wait and how far should i look.' \
           '\nJust click buttons below to configure your settings' \
           '\nList of all commands: /help\n' \
           'Your current settings: /settings'
help_msg = '/wonnaride' + '\n/settings' + '\n/set_radius' + '\n/set_category' + '\n/set_waiting_time' + \
           '\n/stop_searching' + '\n/save_location' + '\n/help' + \
           '\nThis section is under development.\nIf you have some questions write it to @bohovis'


def user_init(bot, s, msg, chat_id):
    uid = None
    if 'username' in msg['from']:
        uid = msg['from']['username']
    nu = Wonnarider(s, chat_id, uid)
    # if not os.path.exists('users.pickle'):
    #     with open('users.pickle', 'w+b') as f:
    #         pickle.dump([nu], f)
    # else:
    #     users = pickle.load(open('users.pickle', 'r+b'))
    #     for u in users:
    #         if u.chat_id == chat_id:
    #             users.remove(u)
    #     users.append(nu)
    #     with open('users.pickle', 'w+b') as f:
    #         pickle.dump(users, f)
    #     del users
    bot.sendMessage(chat_id, init_msg, reply_markup=nu.unsettedParams())
    nu.db_instance.status = s.query(Status).get(2)
    s.commit()


def command_handler(bot, s, u, cm):
    if cm not in command_list:
        # TODO: Some help text
        bot.sendMessage(u.chat_id, 'Unknown command\n*Some help text*')
        return
    elif cm == '/wonnaride':
        # TODO: Check and request for None Params
        if u.location:
            u.setPrevCommand(cm)
            handleLocation(u, s, u.db_instance.location, bot)
            return

        if not (u.ride_type and u.exp_time and u.radius):
            bot.sendMessage(u.chat_id, 'Please complete all of the requirement settings',
                            reply_markup=u.unsettedParams())
            return

        keyboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Send my location to WONNARIDEbot',
                                                                 request_location=True)]])
        bot.sendMessage(u.chat_id, "Share your location so i know where to search for people", reply_markup=keyboard)
        u.setPrevCommand(cm)

    elif cm == '/settings':
        bot.sendMessage(u.chat_id, u.about())

    elif cm == '/set_radius':
        u.setPrevCommand(cm)
        bot.sendMessage(u.chat_id, "Set choose radius in kilometers (1 - 50)", reply_markup=ReplyKeyboardRemove())

    elif cm == '/set_waiting_time':
        u.setPrevCommand(cm)
        bot.sendMessage(u.chat_id, "Please enter the time in hours (it can be not integer) which you want to"
                                   "wait for other riders", reply_markup=ReplyKeyboardRemove())

    elif cm == '/set_category':
        keys = []
        for ride in ride_types:
            keys.append([ride])

        keyboard = ReplyKeyboardMarkup(keyboard=keys)
        bot.sendMessage(u.chat_id, "Select type of your ride", reply_markup=keyboard)

        u.setPrevCommand(cm)

    elif cm == '/save_location':
        keys = [[KeyboardButton(text='Yeah!'), KeyboardButton(text='Nah!')]]

        keyboard = ReplyKeyboardMarkup(keyboard=keys)
        bot.sendMessage(u.chat_id, "Should i save your location after you quit the queue,"
                                   " so i wouldn't ask it again", reply_markup=keyboard)

        u.setPrevCommand(cm)

    elif cm == '/stop_searching':
        u.db_instance.status = s.query(Status).get(2)
        s.commit()
        # if u in active_wonnariders:
        #     active_wonnariders.remove(u)
        u.quitQueue()
        # if u not in semiacive_wonnariders:
        #     semiacive_wonnariders.append(u)

        bot.sendMessage(u.chat_id, 'Now you not searching', reply_markup=u.unsettedParams())

    elif cm == '/help':
        bot.sendMessage(u.chat_id, help_msg, reply_markup=u.unsettedParams())

    elif cm == '/test':
        bot.sendMessage(u.chat_id, u.tagName())


def getUserById(s, id):
    u = Wonnarider(s, db_instance=s.query(User).filter(User.chat_id == id).first())
    # for u in active_wonnariders:
    #     if u.chat_id == id:
    #         u.refreshLastRequestTime()
    #         return u
    # for u in semiacive_wonnariders:
    #     if u.chat_id == id:
    #         u.refreshLastRequestTime()
    #         return u
    # for u in pickle.load(open(userspath, 'r+b')):
    #     if u.chat_id == id:
    #         u.refreshLastRequestTime()
    #         semiacive_wonnariders.append(u)
    return u


def getActiveRiders(s):
    riders = []
    dbriders = s.query(Status).get(1).users
    for r in dbriders:
        riders.append(Wonnarider(s, db_instance=r))
    return riders


def handleLocation(u, s, l, bot):
    u.setLocation(l)
    pprint(l)
    if u.prev_command == '/wonnaride':
        u.setPrevCommand(None)
        u.db_instance.status = s.query(Status).get(1)
        s.commit()
        # if u in semiacive_wonnariders:
        #     semiacive_wonnariders.remove(u)
        u.startSearch()
        nearbyRiders = []
        for r in getActiveRiders(s):
            if r.chat_id != u.chat_id:
                if great_circle(r.location, u.location).km < min(r.radius, u.radius) and \
                        r.isActive() and r != u and r.ride_type == u.ride_type:
                    nearbyRiders.append(r)
        # if u not in active_wonnariders:
        #     active_wonnariders.append(u)
        if not nearbyRiders:
            bot.sendMessage(u.chat_id, 'Wait...', reply_markup=u.quitQueueKeyboard())
        elif len(nearbyRiders) == 1:
            text = 'This dude wants to ride too!\n' + nearbyRiders[0].tagName()
            bot.sendMessage(u.chat_id, text, reply_markup=u.quitQueueKeyboard())
        else:
            text = 'This guys wants to ride!'
            for r in nearbyRiders:
                if r.uid:
                    text += '\n' + r.tagName()
            bot.sendMessage(u.chat_id, text, reply_markup=u.quitQueueKeyboard())
        for r in nearbyRiders:
            bot.sendMessage(r.chat_id, 'New guy appear and he/she wants to ride!\n'+u.tagName())


def twoStepCommandHandler(bot, s, u, text):
    if u.prev_command == '/set_radius':
        # TODO: Some more checks
        try:
            r = float(text)
            if r < 1 or r > 50:
                bot.sendMessage(u.chat_id, 'Please, select radius between 1 and 50 kilometers',
                                reply_markup=u.unsettedParams())
                return
        except ValueError:
            bot.sendMessage(u.chat_id, val_err_msg, reply_markup=u.unsettedParams())
            u.setPrevCommand(None)
            return
        u.setRadius(r)
        bot.sendMessage(u.chat_id, 'Search radius was set to: ' + str(u.radius),
                        reply_markup=u.unsettedParams())
        # u.prev_command = None
    elif u.prev_command == '/set_category':
        if text not in ride_types:
            bot.sendMessage(u.chat_id, 'Pleas select following types!')
            return
        else:
            u.setRideType(text)
            bot.sendMessage(u.chat_id, 'You have selected %s' % text, reply_markup=u.unsettedParams())

    elif u.prev_command == '/save_location':
        if text not in ['Yeah!', 'Nah!']:
            bot.sendMessage(u.chat_id, 'Please, just hit the button!',
                            reply_markup=u.unsettedParams())
            return
        else:
            u.setSaveLoc(True if text == 'Yeah!' else False)
            bot.sendMessage(u.chat_id, 'You have selected %s' % text, reply_markup=u.unsettedParams())

    elif u.prev_command == '/set_waiting_time':
        try:
            ftime = float(text)
            if ftime > 3 or ftime < 0:
                bot.sendMessage(u.chat_id, 'Please, select positive waiting time below 3 hours',
                                reply_markup=u.unsettedParams())
                return
        except ValueError:
            bot.sendMessage(u.chat_id, val_err_msg, reply_markup=u.unsettedParams())
            u.setPrevCommand(None)
            return
        hours = int(ftime)
        minutes = int((ftime-hours)*60)
        u.setExpTime(hours, minutes)
        bot.sendMessage(u.chat_id, 'Your waiting time is: ' + str(u.exp_time), reply_markup=u.unsettedParams())

    u.setPrevCommand(None)


