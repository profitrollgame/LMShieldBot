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

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(["start", "help"], prefixes="/"))
def start(app, msg):

    from_user = msg.from_user

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    keyboard_markup = defaultKeyboard(msg.from_user.id)

    if msg.from_user.id in configGet("admins"):
        msg.reply_text(locale("start_admin", "msg").format(from_user.first_name), reply_markup=keyboard_markup)
    else:
        msg.reply_text(locale("start", "msg").format(from_user.first_name), reply_markup=keyboard_markup)

    if f"{from_user.id}.json" not in os.listdir("data/users/"):
        userSave(
            from_user.id,
            from_user.first_name,
            from_user.last_name,
            from_user.username,
            from_user.phone_number,
            from_user.language_code
        )
        jsonSave(
            f"data/users/{from_user.id}.json",
            {"context": {"action": None, "data": None}}
        )
    
    if from_user.id not in configGet("admins"):
        with open('data/users.txt', 'r', encoding='utf-8') as f:
            if str(msg.from_user.id) not in f.read():
                f.close()
                with open('data/users.txt', 'a', encoding='utf-8') as f:
                    f.write(str(msg.from_user.id)+"\n")
                    f.close()

#===========================================================================================================================

@app.on_message(filters.command(["kill", "die"], prefixes="/"))
def kill(app, msg):

    if msg.from_user.id == configGet("ownerid"):
        msg.reply_text(f"Shutting down bot with pid `{pid}`")
        os.system('kill -9 '+str(pid))

if __name__ == "__main__":

    print(f'[{getDateTime(time.time())}] Starting with PID {str(pid)}')

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

    channels_thread = threading.Thread(target=fetch_channels, name="Channel Fetcher")
    channels_thread.start()

    idle()

    app.send_message(configGet("ownerid"), f"Shutting down bot with pid `{pid}`")
    print(f'\n[{getDateTime(time.time())}] Shutting down with PID {pid}')

    subprocess.call(f'kill -9 {pid}', shell=True)