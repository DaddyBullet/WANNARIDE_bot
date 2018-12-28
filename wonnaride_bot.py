# !/usr/bin/python3
# -*- coding: utf-8 -*- #

import sys
import time
import pickle
from datetime import datetime, timedelta
from flask import Flask, request
from json import dumps

from pprint import pprint
import telepot
from geopy import Point
from telepot.loop import MessageLoop, OrderedWebhook

from wonnaride_core.handlers import command_handler, getUserById,\
    handleLocation, twoStepCommandHandler, user_init, getActiveRiders
from wonnaride_core.handlers import active_wonnariders, semiacive_wonnariders
from wonnaride_core.wonnarider import connect_to_db
from wonnaride_core.wonnarider import Status


def getCommand(msg):
    if 'entities' in msg:
        for e in msg['entities']:
            if e['type'] == 'bot_command':
                return msg['text'][e['offset']:e['offset']+e['length']]
    return None


Session = connect_to_db()
session1 = Session()
session = Session()


def handle(msg, s=session1):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id, msg['from'])

    if content_type == 'text':
        command = getCommand(msg)
        if command == '/start':
            user_init(bot, s, msg, chat_id)
        elif command:
            u = getUserById(s, chat_id)
            command_handler(bot, s, u, command)
            del u
        else:
            u = getUserById(s, chat_id)
            if u.prev_command:
                twoStepCommandHandler(bot, s, u, msg['text'])
            else:
                bot.sendMessage(chat_id, 'Some help text')
            del u

    if content_type == 'location':
        u = getUserById(s, chat_id)
        handleLocation(u, s,
                       dumps(msg["location"]),
                       bot)
        # handleLocation(u, s,
        #                Point(longitude=msg['location']['longitude'], latitude=msg['location']['latitude']),
        #                bot)
        del u


TOKEN = sys.argv[1]  # get token from command-line
# PORT = int(sys.argv[2])
# URL = sys.argv[3]

# app = Flask(__name__)
bot = telepot.Bot(TOKEN)
# webhook = OrderedWebhook(bot, {'chat': on_chat_message})
# @app.route('/webhook', methods=['GET', 'POST'])
# def pass_update():
#     webhook.feed(request.data)
#     return 'OK'
#
# if __name__ == '__main__':
#     try:
#         bot.setWebhook(URL)
#     except telepot.exception.TooManyRequestsError:
#         pass
#     webhook.run_as_thread()
#     app.run(port=PORT, debug=True)
MessageLoop(bot, handle).run_as_thread()
print('Listening ...')


# Keep the program running.
while 1:
    time.sleep(9.5)

    # Checking time expiration
    #
    # pprint(active_wonnariders)
    # pprint("----------------")
    # pprint(semiacive_wonnariders)

    for u in getActiveRiders(session):
        if u.start_time + u.exp_time < datetime.now():
            u.db_instance.status = session.query(Status).get(2)
            session.commit()
            bot.sendMessage(u.chat_id, "You time expire", reply_markup=u.unsettedParams())
            if not u.save_location:
                u.setLocation(None)
            # semiacive_wonnariders.append(u)
    for u in session.query(Status).get(1).users:
        if u.last_request + timedelta(days=7) < datetime.now():
            u.status = session.query(Status).get(3)
            session.commit()
            # semiacive_wonnariders.remove(u)
            # users = pickle.load(open('users.pickle', 'r+b'))
            # for us in users:
            #     if us.chat_id == u.chat_id:
            #         users.remove(us)
            # users.append(u)
            # with open('users.pickle', 'w+b') as f:
            #     pickle.dump(users, f)
            # del users

