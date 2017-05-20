# !/usr/bin/python3
# -*- coding: utf-8 -*- #

import pickle
import os.path
from pprint import pprint
from geopy.distance import great_circle
from wonnaride_core.wonnarider import Wonnarider

active_wonnariders = []
semiacive_wonnariders = []
ride_types = ['bicycle', 'fix', 'bmx', 'roller_blades']
command_list = ['/wonnaride', '/parameters', '/setradius', '/test']
userspath = 'users.pickle'

init_msg = 'Hi! *Some about text...* \nTo start using configure next parameters...'

def user_init(bot, msg, chat_id):
    bot.sendMessage(chat_id, init_msg)
    uid = None
    if 'username' in msg['from']:
        uid = msg['from']['username']
    nu = Wonnarider(chat_id, uid)
    if not os.path.exists('users.pickle'):
        with open('users.pickle', 'w+b') as f:
            pickle.dump([nu], f)
    else:
        users = pickle.load(open('users.pickle', 'r+b'))
        for u in users:
            if u.chat_id == chat_id:
                users.remove(u)
        users.append(nu)
        with open('users.pickle', 'w+b') as f:
            pickle.dump(users, f)
        del users
    semiacive_wonnariders.append(nu)


def command_handler(bot, u, cm):
    if cm not in command_list:
        # TODO: Some help text
        bot.sendMessage(u.chat_id, 'Unknown command\n*Some help text*')
        return
    elif cm == '/wonnaride':
        u.startSearch()
        nearbyRiders = []
        # TODO: Search depend on type
        for r in active_wonnariders:
            if great_circle(r.location, u.location).km < min(r.radius, u.radius) and r.isActive() and r != u:
                nearbyRiders.append(r)
        if u in semiacive_wonnariders:
            semiacive_wonnariders.remove(u)
        if u not in active_wonnariders:
            active_wonnariders.append(u)
        if not nearbyRiders:
            bot.sendMessage(u.chat_id, 'Wait...')
        elif len(nearbyRiders) == 1:
            text = 'This dude wants to ride too!\n' + nearbyRiders[0].tagName()
            bot.sendMessage(u.chat_id, text)
        else:
            text = 'This guys wants to ride!'
            for r in nearbyRiders:
                if r.uid:
                    text += '\n' + r.tagName()
            bot.sendMessage(u.chat_id, text)
        for r in nearbyRiders:
            bot.sendMessage(r.chat_id, 'New guy appear and he/she wants to ride!\n'+u.tagName())

    elif cm == '/parameters':
        bot.sendMessage(u.chat_id, u.about())

    elif cm == '/setradius':
        u.setPrevCommand(cm)
        bot.sendMessage(u.chat_id, "Set choose radius in kilometers (1 - 50)")

    elif cm == '/test':
        bot.sendMessage(u.chat_id, u.tagName())


def getUserById(id):
    for u in active_wonnariders:
        if u.chat_id == id:
            u.refreshLastRequestTime()
            return u
    for u in semiacive_wonnariders:
        if u.chat_id == id:
            u.refreshLastRequestTime()
            return u
    for u in pickle.load(open(userspath, 'r+b')):
        if u.chat_id == id:
            u.refreshLastRequestTime()
            semiacive_wonnariders.append(u)
            return u


def handleLocation(u, l):
    if u in semiacive_wonnariders:
        semiacive_wonnariders.remove(u)
    u.setLocation(l)
    semiacive_wonnariders.append(u)
    pprint(l)


def twoStepCommandHandler(bot, u, text):
    if u.prev_command == '/setradius':
        # TODO: Some more checks
        r = float(text)
        u.setRadius(r)
        bot.sendMessage(u.chat_id, 'Search radius was set to: ' + str(u.radius))
        u.prev_command = None