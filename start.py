import sys
import time
import telepot
from pprint import pprint
from telepot.loop import MessageLoop
import pickle
from wonnarider import Wonnarider
import os.path

init_msg = 'Hi! *Some about text...* \nTo start using configure next parameters...'

active_wonnariders = []
def getUserById(id):
    for u in active_wonnariders:
        if u.chat_id == id:
            return u
    for u in pickle.load(open('users.pickle', 'r+b')):
        if u.chat_id == id:
            active_wonnariders.append(u)
            return u


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        if 'entities' in msg:
            if msg['text'] == '/start':
                bot.sendMessage(chat_id, init_msg)
                nu = Wonnarider(chat_id)
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
                        bot.sendMessage(chat_id, 'Hi one more time')
                    del users

            elif msg['text'] == '/wonnaride':
                u = getUserById(chat_id)
                # TODO: Lot of checks
                u.start_time = time.time()
                wonnariders = u.findWonnariders()

    if content_type == 'location':
        pprint(msg['location'])

TOKEN = sys.argv[1]  # get token from command-line

bot = telepot.Bot(TOKEN)
MessageLoop(bot, handle).run_as_thread()
print ('Listening ...')

# Keep the program running.
while 1:
    time.sleep(10)