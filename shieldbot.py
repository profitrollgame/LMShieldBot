from distutils.command.config import config
import os
from random import random
from random import choice
import time
import _thread
import threading
import subprocess
import traceback
import schedule

from telegram import ForceReply
from functions import *
from pyrogram import Client, filters, idle
from pyrogram import errors
from pyrogram.errors import FloodWait
from pyrogram.types import ChatPermissions, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ChatEventFilter, ForceReply


pid = os.getpid()
app = Client("LordsMobile_Shield_Bot")

def remind_shields():

    global app

    

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(["start", "help"], prefixes="/"))
def start(app, msg):

    from_user = msg.from_user

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if f"{from_user.id}.json" not in os.listdir("data/users/"):
        jsonSave(
            f"data/users/{from_user.id}.json",
            {"locale": None, "shield": None, "active": False}
        )

    if from_user.language_code in jsonLoad("strings.json"):
        userSet(from_user.id, "locale", from_user.language_code)
        send_msg = False
    else:
        send_msg = True
        userSet(from_user.id, "locale", "en")

    msg.reply_text(locale("start", "msg", userid=from_user.id).format(from_user.first_name), reply_markup=defaultKeyboard(userid=from_user.id))

    if send_msg:
        msg.reply_text(locale("translation", "msg", userid=from_user.id))

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(locale("shield_4h", "btn", userid="all"), prefixes=""))
def shield_4h(app, msg):

    from_user = msg.from_user

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if not userGet(from_user.id, "active"):

        userSet(from_user.id, "active", True)

        msg.reply_text("Henlo", reply_markup=activeKeyboard(userid=from_user.id))

    else:

        msg.reply_text("Shield already active")

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(locale("shield_reset", "btn", userid="all"), prefixes=""))
def shield_reset(app, msg):

    from_user = msg.from_user

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if userGet(from_user.id, "active"):

        userSet(from_user.id, "active", False)

        msg.reply_text("Reset", reply_markup=defaultKeyboard(userid=from_user.id))
    
    else:

        msg.reply_text("No active shield")

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(locale("shield_duration", "btn", userid="all"), prefixes=""))
def shield_duration(app, msg):

    from_user = msg.from_user

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if userGet(from_user.id, "active"):

        msg.reply_text("Duration: ...")
    
    else:

        msg.reply_text("No active shield")

#===========================================================================================================================

@app.on_message(filters.command(["kill", "die"], prefixes="/"))
def kill(app, msg):

    if msg.from_user.id == configGet("ownerid"):
        msg.reply_text(f"Shutting down bot with pid `{pid}`")
        os.system('kill -9 '+str(pid))

if __name__ == "__main__":

    print(f'[{getDateTime(time.time())}] Starting with PID {str(pid)}')

    os.makedirs("data/users", exist_ok = True)

    def background_task():
        global pid
        try:
            while True:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except:
                    pass

        except KeyboardInterrupt:
            print('\nShutting down')
            os.system('kill -9 '+str(pid))

    t = threading.Thread(target=background_task)
    t.start()

    app.start()
    app.send_message(configGet("ownerid"), f"Starting bot with pid `{pid}`")

    reminders_thread = threading.Thread(target=remind_shields, name="Shields reminder")
    reminders_thread.start()

    idle()

    app.send_message(configGet("ownerid"), f"Shutting down bot with pid `{pid}`")
    print(f'\n[{getDateTime(time.time())}] Shutting down with PID {pid}')

    subprocess.call(f'kill -9 {pid}', shell=True)