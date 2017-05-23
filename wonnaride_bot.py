# !/usr/bin/python3
# -*- coding: utf-8 -*- #

import sys
import time
import pickle
from datetime import datetime, timedelta

import telepot
from geopy import Point
from telepot.loop import MessageLoop

from wonnaride_core.handlers import command_handler, getUserById,\
    handleLocation, twoStepCommandHandler, user_init, active_wonnariders, semiacive_wonnariders


def getCommand(msg):
    if 'entities' in msg:
        for e in msg['entities']:
            if e['type'] == 'bot_command':
                return msg['text'][e['offset']:e['offset']+e['length']]
    return None


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id, msg['from'])

    if content_type == 'text':
        command = getCommand(msg)
        if command == '/start':
            user_init(bot, msg, chat_id)
        elif command:
            command_handler(bot, getUserById(chat_id), command)
        else:
            u = getUserById(chat_id)
            if u.prev_command:
                twoStepCommandHandler(bot, u, msg['text'])
            else:
                bot.sendMessage(chat_id, 'Some help text')

    if content_type == 'location':
        handleLocation(getUserById(chat_id),
                       Point(longitude=msg['location']['longitude'], latitude=msg['location']['latitude']),
                       bot)

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')

# Keep the program running.
while 1:
    time.sleep(9.5)

    # Checking time expiration
    for u in active_wonnariders:
        if u.start_time + u.exp_time < datetime.now():
            active_wonnariders.remove(u)
            if not u.save_location:
                u.setLocation(None)
            semiacive_wonnariders.append(u)
    for u in semiacive_wonnariders:
        if u.last_request + timedelta(days=1) < datetime.now():
            semiacive_wonnariders.remove(u)
            users = pickle.load(open('users.pickle', 'r+b'))
            for us in users:
                if us.chat_id == u.chat_id:
                    users.remove(us)
            users.append(u)
            with open('users.pickle', 'w+b') as f:
                pickle.dump(users, f)
            del users

