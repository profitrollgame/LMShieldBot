import asyncio
from datetime import datetime
from datetime import timedelta
from pathlib import Path
from distutils.command.config import config
import os
from random import random
from random import choice
import time
import _thread
import threading
import subprocess
import traceback

from telegram import ForceReply
from functions import *
from timeformat import strfdelta
from pyrogram import Client, filters, idle
from pyrogram import errors
from pyrogram.errors import FloodWait
from pyrogram.types import ChatPermissions, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton, ChatEventFilter, ForceReply


pid = os.getpid()
app = Client("LordsMobile_Shield_Bot")

def nowStamp():
    return int(datetime.timestamp(datetime.now()))

def reminderAdd(userid, intime):
    reminders = jsonLoad("data/reminders.json")
    reminders_index = jsonLoad("data/reminders_index.json")

    if str(userid) not in reminders_index:
        reminders_index[str(userid)] = []

    if str(intime) not in reminders:
        reminders[str(intime)] = []

    if not isinstance(reminders_index[str(userid)], list):
        reminders_index[str(userid)] = []
    reminders_index[str(userid)].append(intime)

    if not isinstance(reminders[str(intime)], list):
        reminders[str(intime)] = []
    reminders[str(intime)].append(userid)

    jsonSave("data/reminders.json", reminders)
    jsonSave("data/reminders_index.json", reminders_index)

def reminderReset(userid):
    shields = jsonLoad("data/shields.json")
    reminders = jsonLoad("data/reminders.json")
    reminders_index = jsonLoad("data/reminders_index.json")

    if str(userGet(userid, "shield")) in shields:
        del shields[str(userGet(userid, "shield"))]

    if str(userid) in reminders_index:
        for ts in reminders_index[str(userid)]:
            reminders[str(ts)].remove(userid)
            if reminders[str(ts)] == []:
                del reminders[str(ts)]
    
    if str(userid) in reminders_index:
        del reminders_index[str(userid)]

    jsonSave("data/shields.json", shields)
    jsonSave("data/reminders.json", reminders)
    jsonSave("data/reminders_index.json", reminders_index)

    userSet(userid, "active", False)
    userSet(userid, "shield", None)


async def reminderSend(userid, message, expired=False):
    global app
    if expired:
        await app.send_message(userid, message, reply_markup=defaultKeyboard(userid))
    else:
        await app.send_message(userid, message)

def remind_shields():

    while True:

        shields = jsonLoad("data/shields.json")
        reminders = jsonLoad("data/reminders.json")
        reminders_index = jsonLoad("data/reminders_index.json")

        now_time = nowStamp()

        if str(now_time) in shields:
            for user in shields[str(now_time)]:
                asyncio.run(reminderSend(user, locale("expired", "msg", user), expired=True))
                reminderReset(user)

        if str(now_time) in reminders:
            for user in reminders[str(now_time)]:
                asyncio.run(reminderSend( user, locale("expiring", "msg", userid=user).format(strfdelta(userGet(user, "shield")-nowStamp(), locale("expiring_format", "msg", userid=user), inputtype="seconds")) ))
                reminders[str(now_time)].remove(user)
                reminders_index[str(user)].remove(now_time)
                jsonSave("data/reminders.json", reminders)
                jsonSave("data/reminders_index.json", reminders)
        
        if configGet("debug"):
            print(now_time)

        time.sleep(1)

def shieldSet(userid, intime):
    userSet(userid, "active", True)
    userSet(userid, "shield", nowStamp()+intime)
    for remtime in configGet("reminders"):
        if intime > remtime:
            reminderAdd(userid, nowStamp()+intime-remtime)
    shields = jsonLoad("data/shields.json")
    if str(nowStamp()+intime) not in shields:
        shields[str(nowStamp()+intime)] = []
    shields[str(nowStamp()+intime)].append(userid)
    jsonSave("data/shields.json", shields)

def shieldStart(app, msg, shieldtime):
    app.send_chat_action(chat_id=msg.chat.id, action="typing")
    if not userGet(msg.from_user.id, "active"):
        userSet(msg.from_user.id, "active", True)
        shieldSet(msg.from_user.id, shieldtime)
        msg.reply_text(locale("shield_4h", "shi", userid=msg.from_user.id), reply_markup=activeKeyboard(userid=msg.from_user.id))
    else:
        msg.reply_text(locale("already_active", "msg", userid=msg.from_user.id))
    appendLog("Started shield for {0} (user {1})".format(strfdelta(shieldtime, "{D}d {H}h {M}m", inputtype="seconds"), msg.from_user.id))

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
    appendLog(f"Start command called (user {from_user.id})")

    if send_msg:
        msg.reply_text(locale("translation", "msg", userid=from_user.id))

@app.on_message(~ filters.scheduled & filters.command(["locale"], prefixes="/"))
def locale_set(app, msg):

    from_user = msg.from_user

    try:
        fullcmd = msg.text.split()
        if fullcmd[1] in jsonLoad("strings.json"):
            userSet(from_user.id, "locale", fullcmd[1])
            if userGet(from_user.id, "active"):
                msg.reply_text(locale("locale_set", "msg", userid=from_user.id), reply_markup=activeKeyboard(userid=from_user.id))
            else:
                msg.reply_text(locale("locale_set", "msg", userid=from_user.id), reply_markup=defaultKeyboard(userid=from_user.id))
            appendLog(f"Locale {fullcmd[1]} is now set as primary (user {from_user.id})")
        else:
            locale_list = []
            locales = jsonLoad("strings.json")
            for loc in locales:
                locale_list.append(f"`{loc}`")
            msg.reply_text(locale("locale_wrong", "msg", userid=from_user.id).format(", ".join(locale_list)))
    except:
        traceback.print_exc()
        msg.reply_text(locale("locale_syntax", "msg", userid=from_user.id))

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(locale("shield_4h", "btn", userid="all"), prefixes=""))
def shield_4h(app, msg):
    shieldStart(app, msg, 4*60*60)

@app.on_message(~ filters.scheduled & filters.command(locale("shield_8h", "btn", userid="all"), prefixes=""))
def shield_8h(app, msg):
    shieldStart(app, msg,  8*60*60)

@app.on_message(~ filters.scheduled & filters.command(locale("shield_24h", "btn", userid="all"), prefixes=""))
def shield_24h(app, msg):
    shieldStart(app, msg, 24*60*60)

@app.on_message(~ filters.scheduled & filters.command(locale("shield_3d", "btn", userid="all"), prefixes=""))
def shield_3d(app, msg):
    shieldStart(app, msg, 3*24*60*60)

@app.on_message(~ filters.scheduled & filters.command(locale("shield_7d", "btn", userid="all"), prefixes=""))
def shield_7d(app, msg):
    shieldStart(app, msg, 7*24*60*60)

@app.on_message(~ filters.scheduled & filters.command(locale("shield_14d", "btn", userid="all"), prefixes=""))
def shield_14d(app, msg):
    shieldStart(app, msg, 14*24*60*60)

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(locale("shield_reset", "btn", userid="all")+["reset"], prefixes=["", "/"]))
def shield_reset(app, msg):

    from_user = msg.from_user

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if userGet(from_user.id, "active"):

        reminderReset(from_user.id)
        msg.reply_text(locale("reset", "msg", userid=from_user.id), reply_markup=defaultKeyboard(userid=from_user.id))
        appendLog(f"Shield has been reset (user {from_user.id})")
    
    else:

        msg.reply_text(locale("no_shield", "msg", userid=from_user.id))

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command(locale("shield_duration", "btn", userid="all")+["duration"], prefixes=["", "/"]))
def shield_duration(app, msg):

    from_user = msg.from_user

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if userGet(from_user.id, "active"):

        msg.reply_text(locale("remain", "msg", userid=from_user.id).format( strfdelta(userGet(from_user.id, "shield")-nowStamp(), locale("remain_format", "msg", userid=from_user.id), inputtype="seconds") ))
        appendLog(f"Sent how long shield remains (user {from_user.id})")
    
    else:

        msg.reply_text(locale("no_shield", "msg", userid=from_user.id))

@app.on_message(~ filters.scheduled & filters.command("shield", prefixes=["", "/"]))
def shield_activate(app, msg):
    app.send_chat_action(chat_id=msg.chat.id, action="typing")
    msg.reply_text("Not ready yet")

#===========================================================================================================================

@app.on_message(filters.command(["kill", "die"], prefixes="/"))
def kill(app, msg):

    if msg.from_user.id == configGet("ownerid"):
        appendLog(f'Shutting down with PID {pid}')
        msg.reply_text(f"Shutting down with pid `{pid}`")
        os.system('kill -9 '+str(pid))

if __name__ == "__main__":

    appendLog(f'Starting with PID {str(pid)}')

    os.makedirs("data/users", exist_ok = True)
    os.makedirs("logs", exist_ok = True)

    if not os.path.exists("data/shields.json"):
        Path("data/shields.json").write_text("{}", encoding="utf-8")

    if not os.path.exists("data/reminders.json"):
        Path("data/reminders.json").write_text("{}", encoding="utf-8")

    if not os.path.exists("data/reminders_index.json"):
        Path("data/reminders_index.json").write_text("{}", encoding="utf-8")

    app.start()
    app.send_message(configGet("ownerid"), f"Starting with pid `{pid}`")

    reminders_thread = threading.Thread(target=remind_shields, name="Shields reminder")
    reminders_thread.start()

    idle()

    app.send_message(configGet("ownerid"), f"Shutting down with pid `{pid}`")
    appendLog(f'Shutting down with PID {pid}')

    subprocess.call(f'kill -9 {pid}', shell=True)