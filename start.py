# !/usr/bin/python3
# -*- coding: utf-8 -*- #

import sys
import time
import telepot
from pprint import pprint
from telepot.loop import MessageLoop
import pickle
from wonnarider import Wonnarider
import os.path
from geopy import Point
from geopy.distance import great_circle

init_msg = 'Hi! *Some about text...* \nTo start using configure next parameters...'

active_wonnariders = []
semiacive_wonnariders = []
ride_types = ['bicycle', 'fix', 'bmx', 'roller_blades']
command_list = ['/wonnaride', '/test']


def command_handler(bot, u, cm):
    if cm not in command_list:
        # TODO: Some help text
        bot.sendMessage(u.chat_id, 'Unknown command/n*Some help text*')
        return
    elif cm == '/wonnaride':
        u.startSearch()
        nearbyRiders = []
        # TODO: Search depend on type
        for r in active_wonnariders:
            if great_circle(r.location, u.location).km < min(r.radius, u.radius):
                nearbyRiders.append(r)
        if u in semiacive_wonnariders:
            semiacive_wonnariders.remove(u)
        if u not in active_wonnariders:
            active_wonnariders.append(u)
        if not nearbyRiders:
            bot.sendMessage(u.chat_id, 'Wait...')
        elif len(nearbyRiders) == 1:
            bot.sendMessage(u.chat_id, 'This dude wants to ride too!')
            bot.sendMessage(u.chat_id, nearbyRiders[0].tagName())
        else:
            bot.sendMessage(u.chat_id, 'This guys wants to ride!')
            for r in nearbyRiders:
                bot.sendMessage(u.chat_id, r.tagName())
        for r in nearbyRiders:
            bot.sendMessage(r.chat_id, 'New guy appear and he/she wants to ride!\n'+u.tagName())

    elif cm == '/test':
        bot.sendMessage(u.chat_id, u.tagName())


def getUserById(id):
    for u in active_wonnariders:
        if u.chat_id == id:
            return u
    for u in semiacive_wonnariders:
        if u.chat_id == id:
            return u
    for u in pickle.load(open('users.pickle', 'r+b')):
        if u.chat_id == id:
            return u


def getCommand(msg):
    if 'entities' in msg:
        for e in msg['entities']:
            if e['type'] == 'bot_command':
                return msg['text'][e['offset']:e['offset']+e['length']]


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id, msg['from'])

    if content_type == 'text':
        command = getCommand(msg)
        if command == '/start':
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
                if chat_id not in [u.chat_id for u in users]:
                    users.append(nu)
                    with open('users.pickle', 'w+b') as f:
                        pickle.dump(users, f)
                else:
                    # TODO: Some ok response
                    bot.sendMessage(chat_id, 'Hi one more time')
                del users
        elif command:
            command_handler(bot, getUserById(chat_id), command)

        else:
            bot.sendMessage(chat_id, 'Some help text')

    if content_type == 'location':
        u = getUserById(chat_id)
        if u in semiacive_wonnariders:
            semiacive_wonnariders.remove(u)
        u.setLocation(Point(longitude=msg['location']['longitude'], latitude=msg['location']['latitude']))
        semiacive_wonnariders.append(u)
        pprint(msg['location'])

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)
