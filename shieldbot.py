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


def advert_send(app, msg, advert):
    
    msg.edit("Рассылка завершена")


def fetch_channels():

    time.sleep(5)

    while True:

        for channel in configGet("channels"):
            memberlist = []
            for member in app.iter_chat_members(channel["id"], filter="all"):
                memberlist.append(member.user.id)
            jsonSave(f"data/channels/{channel['id']}.json", {"members": memberlist})
            time.sleep(2)

        time.sleep(30)

#===========================================================================================================================

@app.on_message(~ filters.scheduled & filters.command([locale("random_movie", "btn"), locale("random_movie_short", "btn")], prefixes=""))
def random_movie(app, msg):

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if userSubscribed(msg.chat.id):
        movies = jsonLoad(f"data/movies.json")["movies"]
        movie = choice(list(movies.keys()))
        movie = movies[movie]
        if movie["description"] != None:
            if movie["link"] != None:
                msg.reply_text(locale("random_entry", "msg").format(movie["title"], movie["description"]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=movie["link"])]]))
            else:
                msg.reply_text(locale("random_entry", "msg").format(movie["title"], movie["description"]))
        else:
            if movie["link"] != None:
                msg.reply_text(locale("random_entry_short", "msg").format(movie["title"]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=movie["link"])]]))
            else:
                msg.reply_text(locale("random_entry_short", "msg").format(movie["title"]))
    else:
        msg.reply_text(locale("sub_required", "msg"), reply_markup=channelsKeyboard())


@app.on_message(~ filters.scheduled & filters.command([locale("random_series", "btn"), locale("random_series_short", "btn")], prefixes=""))
def random_series(app, msg):

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if userSubscribed(msg.chat.id):
        series = jsonLoad(f"data/movies.json")["series"]
        serie = choice(list(series.keys()))
        serie = series[serie]
        if serie["description"] != None:
            if serie["link"] != None:
                msg.reply_text(locale("random_entry", "msg").format(serie["title"], serie["description"]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=serie["link"])]]))
            else:
                msg.reply_text(locale("random_entry", "msg").format(serie["title"], serie["description"]))
        else:
            if serie["link"] != None:
                msg.reply_text(locale("random_entry_short", "msg").format(serie["title"]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=serie["link"])]]))
            else:
                msg.reply_text(locale("random_entry_short", "msg").format(serie["title"]))
    else:
        msg.reply_text(locale("sub_required", "msg"), reply_markup=channelsKeyboard())


@app.on_message(~ filters.scheduled & filters.command([locale("search", "btn"), locale("search_short", "btn")], prefixes=""))
def find_movie(app, msg):

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    if userSubscribed(msg.chat.id):
        newmsg = msg.reply_text(locale("search_input", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True)) #ForceReply(placeholder=locale("search", "fry")))
        userSet(msg.chat.id, "context", "search")
        userSet(msg.chat.id, "context_content", newmsg.message_id)
    else:
        msg.reply_text(locale("sub_required", "msg"), reply_markup=channelsKeyboard())


@app.on_message(~ filters.scheduled & filters.command([locale("cancel", "btn"), "/cancel"], prefixes=""))
def cancel(app, msg):

    app.send_chat_action(chat_id=msg.chat.id, action="typing")

    userClear(msg.from_user.id, "context")
    userClear(msg.from_user.id, "context_content")

    keyboard_markup = defaultKeyboard(msg.from_user.id)

    msg.reply_text(locale("cancel", "msg"), reply_markup=keyboard_markup)

#===========================================================================================================================


@app.on_message(~ filters.scheduled & filters.command([locale("userbase", "btn")], prefixes=""))
def userbase(app, msg):
    if msg.from_user.id in configGet("admins"):
        app.send_chat_action(chat_id=msg.chat.id, action="upload_document")
        with open("data/users.txt") as f:
            usercount = sum(1 for _ in f)
        msg.reply_document("data/users.txt", caption=locale("userbase", "msg").format(str(usercount)))


@app.on_message(~ filters.scheduled & filters.command([locale("list_movies", "btn")], prefixes=""))
def list_movies(app, msg):
    if msg.from_user.id in configGet("admins"):
        app.send_chat_action(chat_id=msg.chat.id, action="upload_document")
        dumpMovies("movies")
        msg.reply_document("tmp/movies.json")

@app.on_message(~ filters.scheduled & filters.command([locale("list_series", "btn")], prefixes=""))
def list_series(app, msg):
    if msg.from_user.id in configGet("admins"):
        app.send_chat_action(chat_id=msg.chat.id, action="upload_document")
        dumpMovies("series")
        msg.reply_document("tmp/series.json")

@app.on_message(~ filters.scheduled & filters.command([locale("list_channels", "btn")], prefixes=""))
def list_channels(app, msg):
    if msg.from_user.id in configGet("admins"):
        app.send_chat_action(chat_id=msg.chat.id, action="upload_document")
        dumpChannels()
        msg.reply_document("tmp/channels.json")


@app.on_message(~ filters.scheduled & filters.command([locale("add_advert", "btn")], prefixes=""))
def advert_content(app, msg):

    if msg.from_user.id in configGet("admins"):

        msg.reply_text(locale("advert_content", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True))
        userSet(msg.chat.id, "context", "advert_content")


@app.on_message(~ filters.scheduled & filters.command([locale("add_channel", "btn")], prefixes=""))
def channel_add(app, msg):

    if msg.from_user.id in configGet("admins"):

        msg.reply_text(locale("channel_add", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True))
        msg.reply_text(locale("channel_guide", "msg").format(locale("channel_guide_url", "clb")), disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("channel_guide", "clb"), url=locale("channel_guide_url", "clb"))]]))
        userSet(msg.chat.id, "context", "channel_add")


@app.on_message(~ filters.scheduled & filters.command([locale("remove_channel", "btn")], prefixes=""))
def channel_remove(app, msg):

    if msg.from_user.id in configGet("admins"):

        msg.reply_text(locale("channel_remove", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True))
        userSet(msg.chat.id, "context", "channel_remove")


@app.on_message(~ filters.scheduled & filters.command([locale("add_movie", "btn")], prefixes=""))
def add_film(app, msg):

    if msg.from_user.id in configGet("admins"):

        msg.reply_text(locale("add_movie_title", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True))
        userSet(msg.chat.id, "context", "add_movie_title")


@app.on_message(~ filters.scheduled & filters.command([locale("add_series", "btn")], prefixes=""))
def add_series(app, msg):

    if msg.from_user.id in configGet("admins"):

        msg.reply_text(locale("add_series_title", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True))
        userSet(msg.chat.id, "context", "add_series_title")


@app.on_message(~ filters.scheduled & filters.command([locale("remove_movie", "btn")], prefixes=""))
def remove_movie(app, msg):

    if msg.from_user.id in configGet("admins"):

        msg.reply_text(locale("remove_movie", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True))
        userSet(msg.chat.id, "context", "remove_movie")


@app.on_message(~ filters.scheduled & filters.command([locale("remove_series", "btn")], prefixes=""))
def remove_series(app, msg):

    if msg.from_user.id in configGet("admins"):

        msg.reply_text(locale("remove_series", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("cancel", "btn")] ], resize_keyboard=True))
        userSet(msg.chat.id, "context", "remove_series")

#===========================================================================================================================


@app.on_message(~ filters.scheduled & filters.command([locale("page_1", "btn")], prefixes=""))
def page_1(app, msg):
    if msg.from_user.id in configGet("admins"):
        msg.reply_text(locale("keyboard_shown", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))

@app.on_message(~ filters.scheduled & filters.command([locale("page_2", "btn")], prefixes=""))
def page_2(app, msg):
    if msg.from_user.id in configGet("admins"):
        msg.reply_text(locale("keyboard_shown", "msg"), reply_markup=secondKeyboard(msg.from_user.id))

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


@app.on_callback_query()
def answer(app, callback):

    if callback.data == "sub_check":

        callback.message.edit(locale("sub_checking", "msg"))
        callback.answer(locale("sub_checking", "msg"))

        for channel in configGet("channels"):
            memberlist = []
            for member in app.iter_chat_members(channel["id"], filter="all"):
                memberlist.append(member.user.id)
            jsonSave(f"data/channels/{channel['id']}.json", {"members": memberlist})
            time.sleep(.5)

        if userSubscribed(callback.from_user.id):
            callback.message.edit(locale("sub_confirmed", "msg"))
        else:
            callback.message.edit(locale("sub_failed", "msg"), reply_markup=channelsKeyboard())

    elif callback.data.startswith("preview_"):

        # try:
        context_content = userGet(callback.from_user.id, "context_content")

        if context_content["button"] != None:
            app.copy_message(chat_id=callback.from_user.id, from_chat_id=int(callback.data.split("_")[1]), message_id=context_content["message"], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(context_content["button"][1], url=context_content["button"][0])]]))
        else:
            app.copy_message(chat_id=callback.from_user.id, from_chat_id=int(callback.data.split("_")[1]), message_id=context_content["message"])

        callback.answer(locale("advert_preview_success", "clb"))

        # except:
        #     callback.answer(locale("advert_preview_failed", "clb"))

    elif callback.data.startswith("iban_payment"):

        reply_string = locale("payment_direct", "msg").format(
            configGet("iban", "payment", "direct"),
            configGet("receiver", "payment", "direct"),
            configGet("itn", "payment", "direct"),
            configGet("reason", "payment", "direct"),
            configGet("amount", "payment")
        )
        callback.answer(locale("payment_direct_shown", "clb"))
        app.send_message(callback.from_user.id, text=reply_string)


@app.on_message(filters.command(["kill", "die"], prefixes="/"))
def kill(app, msg):

    if msg.from_user.id == 277862475:
        msg.reply_text(f"Shutting down bot with pid `{pid}`")
        os.system('kill -9 '+str(pid))


@app.on_message(~ filters.scheduled)
def any_message_handler(app, msg):

    if userGet(msg.from_user.id, "context") == "search":

        if len(msg.text) > 2:

            search_result = []

            movies_dict = jsonLoad(f"data/movies.json")["movies"]
            series_dict = jsonLoad(f"data/movies.json")["series"]

            for entry in series_dict:

                if msg.text.lower() in series_dict[entry]["title"].lower():

                    if series_dict[entry]["link"] != None:
                        res = f'• **[{series_dict[entry]["title"]}]({series_dict[entry]["link"]})**'
                    else:
                        res = f'• **{series_dict[entry]["title"]}**'

                    if series_dict[entry]["description"] != None:
                        res += f'\n{series_dict[entry]["description"]}'

                    search_result.append(res)

                elif msg.text == entry:

                    userClear(msg.from_user.id, "context")

                    if series_dict[entry]["description"] != None:
                        if series_dict[entry]["link"] != None:
                            msg.reply_text(locale("found_series", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))
                            msg.reply_text(locale("found_entry", "msg").format(series_dict[entry]["title"], series_dict[entry]["description"]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=series_dict[entry]["link"])]]))
                        else:
                            msg.reply_text(locale("found_entry", "msg").format(series_dict[entry]["title"], series_dict[entry]["description"]), reply_markup=defaultKeyboard(msg.from_user.id))
                    else:
                        if series_dict[entry]["link"] != None:
                            msg.reply_text(locale("found_series", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))
                            msg.reply_text(locale("found_entry_short", "msg").format(series_dict[entry]["title"]), reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=series_dict[entry]["link"])]]))
                        else:
                            msg.reply_text(locale("found_entry_short", "msg").format(series_dict[entry]["title"]), reply_markup=defaultKeyboard(msg.from_user.id))

                    return

            for entry in movies_dict:

                if msg.text.lower() in movies_dict[entry]["title"].lower():

                    if movies_dict[entry]["description"] != None:
                        search_result.append(f'• **[{movies_dict[entry]["title"]}]({movies_dict[entry]["link"]})**\n{movies_dict[entry]["description"]}')
                    else:
                        search_result.append(f'• **[{movies_dict[entry]["title"]}]({movies_dict[entry]["link"]})**')

                elif msg.text == entry:

                    userClear(msg.from_user.id, "context")

                    if movies_dict[entry]["description"] != None:
                        if movies_dict[entry]["link"] != None:
                            msg.reply_text(locale("found_movie", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))
                            msg.reply_text(locale("found_entry", "msg").format(movies_dict[entry]["title"], movies_dict[entry]["description"]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=movies_dict[entry]["link"])]]))
                        else:
                            msg.reply_text(locale("found_entry", "msg").format(movies_dict[entry]["title"], movies_dict[entry]["description"]), reply_markup=defaultKeyboard(msg.from_user.id))
                    else:
                        if movies_dict[entry]["link"] != None:
                            msg.reply_text(locale("found_movie", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))
                            msg.reply_text(locale("found_entry_short", "msg").format(movies_dict[entry]["title"]), reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(locale("watch_online", "clb"), url=movies_dict[entry]["link"])]]))
                        else:
                            msg.reply_text(locale("found_entry_short", "msg").format(movies_dict[entry]["title"]), reply_markup=defaultKeyboard(msg.from_user.id))
                        
                    return

            if search_result != []:
                msg.reply_text(locale("search_result", "msg") + "\n\n" + "\n\n".join(search_result), disable_web_page_preview=True, reply_markup=defaultKeyboard(msg.from_user.id))
            else:
                msg.reply_text(locale("search_none", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))

        else:

            msg.reply_text(locale("search_short", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))

        userClear(msg.from_user.id, "context")

    #=======================================================================================================================

    elif userGet(msg.from_user.id, "context") == "add_movie_title":

        userSet(msg.from_user.id, "context", "add_movie_number")
        userSet(msg.from_user.id, "context_content", {"type": "movie", "title": msg.text, "number": None, "description": None, "link": None})

        msg.reply_text(locale("add_movie_number", "msg"))

    elif userGet(msg.from_user.id, "context") == "add_movie_number":

        userSet(msg.from_user.id, "context", "add_movie_description")
        user_context = userGet(msg.from_user.id, "context_content")
        user_context["number"] = msg.text
        userSet(msg.from_user.id, "context_content", user_context)

        msg.reply_text(locale("add_movie_description", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("no_description", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

    elif userGet(msg.from_user.id, "context") == "add_movie_description":

        user_context = userGet(msg.from_user.id, "context_content")

        if msg.text == locale("no_description", "btn"):
            userSet(msg.from_user.id, "context", "add_movie_link")
            user_context["description"] = None
            userSet(msg.from_user.id, "context_content", user_context)

            msg.reply_text(locale("add_movie_link", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("no_link", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

        else:
            userSet(msg.from_user.id, "context", "add_movie_link")
            user_context["description"] = msg.text
            userSet(msg.from_user.id, "context_content", user_context)

            msg.reply_text(locale("add_movie_link", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("no_link", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

    elif userGet(msg.from_user.id, "context") == "add_movie_link":

        user_context = userGet(msg.from_user.id, "context_content")

        if msg.text == locale("no_link", "btn"):
            user_context["link"] = None
        else:
            user_context["link"] = msg.text

        movies = jsonLoad("data/movies.json")

        movies["movies"][user_context["number"]] = {"title": user_context["title"], "link": user_context["link"], "description": user_context["description"]}
        jsonSave("data/movies.json", movies)
        userClear(msg.from_user.id, "context")
        userClear(msg.from_user.id, "context_content")

        msg.reply_text(locale("add_movie_success", "msg").format( user_context["number"], user_context["title"], user_context["link"], user_context["description"] ), reply_markup=defaultKeyboard(msg.from_user.id))

    #=======================================================================================================================

    elif userGet(msg.from_user.id, "context") == "add_series_title":

        userSet(msg.from_user.id, "context", "add_series_number")
        userSet(msg.from_user.id, "context_content", {"type": "series", "title": msg.text, "number": None, "description": None, "link": None})

        msg.reply_text(locale("add_series_number", "msg"))

    elif userGet(msg.from_user.id, "context") == "add_series_number":

        userSet(msg.from_user.id, "context", "add_series_description")
        user_context = userGet(msg.from_user.id, "context_content")
        user_context["number"] = msg.text
        userSet(msg.from_user.id, "context_content", user_context)

        msg.reply_text(locale("add_series_description", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("no_description", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

    elif userGet(msg.from_user.id, "context") == "add_series_description":

        user_context = userGet(msg.from_user.id, "context_content")

        if msg.text == locale("no_description", "btn"):
            userSet(msg.from_user.id, "context", "add_series_link")
            user_context["description"] = None
            userSet(msg.from_user.id, "context_content", user_context)

            msg.reply_text(locale("add_series_link", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("no_link", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

        else:
            userSet(msg.from_user.id, "context", "add_series_link")
            user_context["description"] = msg.text
            userSet(msg.from_user.id, "context_content", user_context)

            msg.reply_text(locale("add_series_link", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("no_link", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

    elif userGet(msg.from_user.id, "context") == "add_series_link":

        user_context = userGet(msg.from_user.id, "context_content")

        if msg.text == locale("no_link", "btn"):
            user_context["link"] = None
        else:
            user_context["link"] = msg.text

        series = jsonLoad("data/movies.json")

        series["series"][user_context["number"]] = {"title": user_context["title"], "link": user_context["link"], "description": user_context["description"]}
        jsonSave("data/movies.json", series)
        userClear(msg.from_user.id, "context")
        userClear(msg.from_user.id, "context_content")

        msg.reply_text(locale("add_series_success", "msg").format( user_context["number"], user_context["title"], user_context["link"], user_context["description"] ), reply_markup=defaultKeyboard(msg.from_user.id))

    #=======================================================================================================================

    elif userGet(msg.from_user.id, "context") == "remove_movie":

        fulldict = jsonLoad(f"data/movies.json")
        movies_dict = fulldict["movies"]

        for entry in movies_dict:
            if msg.text == entry:
                msg.reply_text(locale("remove_movie_success", "msg").format(movies_dict[entry]["title"]), reply_markup=defaultKeyboard(msg.from_user.id))
                userClear(msg.from_user.id, "context")
                del movies_dict[entry]
                fulldict["movies"] = movies_dict
                jsonSave("data/movies.json", fulldict)
                return

        msg.reply_text(locale("remove_movie_failed", "msg").format(msg.text), reply_markup=defaultKeyboard(msg.from_user.id))
        userClear(msg.from_user.id, "context")

    elif userGet(msg.from_user.id, "context") == "remove_series":

        fulldict = jsonLoad(f"data/movies.json")
        series_dict = fulldict["series"]

        for entry in series_dict:
            if msg.text == entry:
                msg.reply_text(locale("remove_series_success", "msg").format(series_dict[entry]["title"]), reply_markup=defaultKeyboard(msg.from_user.id))
                userClear(msg.from_user.id, "context")
                del series_dict[entry]
                fulldict["series"] = series_dict
                jsonSave("data/movies.json", fulldict)
                return

        msg.reply_text(locale("remove_series_failed", "msg").format(msg.text), reply_markup=defaultKeyboard(msg.from_user.id))
        userClear(msg.from_user.id, "context")

    #=======================================================================================================================

    elif userGet(msg.from_user.id, "context") == "advert_content":

        userSet(msg.from_user.id, "context", "advert_button")
        userSet(msg.from_user.id, "context_content", {"message": msg.message_id, "button": None})

        msg.reply_text(locale("advert_button", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("no_button", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

    elif userGet(msg.from_user.id, "context") == "advert_button":

        if msg.text != locale("no_button", "btn"):
            user_context = userGet(msg.from_user.id, "context_content")
            user_context["button"] = msg.text.split("\n")
            userSet(msg.from_user.id, "context_content", user_context)

        userSet(msg.from_user.id, "context", "advert_ready")
        
        msg.reply_text(locale("advert_confirm", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("confirm", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))

        msg.reply_text(locale("advert_preview", "msg"), reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(locale("advert_preview", "clb"), callback_data=f'preview_{msg.from_user.id}')]
        ]))

    elif userGet(msg.from_user.id, "context") == "advert_ready":

        if msg.text == locale("confirm", "btn"):
            msg.reply_text(locale("advert_started", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))
            #_thread.start_new_thread(advert_send, (app, new_msg, userGet(msg.from_user.id, "context_content")))
            sent_msgs = 0
            context_content = userGet(msg.from_user.id, "context_content")
            #with open("data/testusers.txt") as f:
            with open("data/users.txt") as f:
                lines = [line.rstrip('\n') for line in f]
            for user in lines:
                try:
                    if context_content["button"] != None:
                        app.copy_message(chat_id=int(user), from_chat_id=msg.from_user.id, message_id=context_content["message"], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(context_content["button"][1], url=context_content["button"][0])]]))
                    else:
                        app.copy_message(chat_id=int(user), from_chat_id=msg.from_user.id, message_id=context_content["message"])
                        sent_msgs += 1
                except:
                    pass
            msg.reply_text(locale("advert_finished", "msg").format(sent_msgs))
            userClear(msg.from_user.id, "context")
            userClear(msg.from_user.id, "context_content")

    elif userGet(msg.from_user.id, "context") == "channel_add":

        try:

            msg_con = msg.text.split("\n")
            chinfo = {"name": msg_con[0], "id": msg_con[1], "link": msg_con[2]}

            if isinstance(channelMembers(app, chinfo["id"]), list):
                msg.reply_text(locale("channel_add_exists", "msg"), reply_markup=ReplyKeyboardMarkup([ [locale("confirm", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))
            else:
                msg.reply_text(locale("channel_add_invalid_channel", "msg").format(locale("channel_guide_url", "clb")), reply_markup=ReplyKeyboardMarkup([ [locale("confirm", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))
            
            userSet(msg.from_user.id, "context", "channel_ready")
            userSet(msg.from_user.id, "context_content", chinfo)

        except:

            msg.reply_text(locale("channel_add_invalid_format", "msg"))

    elif userGet(msg.from_user.id, "context") == "channel_remove":

        for channel in configGet("channels"):

            if msg.text == channel["id"]:
                userSet(msg.from_user.id, "context", "channel_remove_ready")
                userSet(msg.from_user.id, "context_content", channel)
                msg.reply_text(locale("channel_remove_found", "msg").format(channel["name"]), reply_markup=ReplyKeyboardMarkup([ [locale("confirm", "btn")], [locale("cancel", "btn")] ], resize_keyboard=True))
                return

        msg.reply_text(locale("channel_remove_none", "msg"), reply_markup=defaultKeyboard(msg.from_user.id))
        userClear(msg.from_user.id, "context")
        userClear(msg.from_user.id, "context_content")

    elif userGet(msg.from_user.id, "context") == "channel_remove_ready":

        if msg.text == locale("confirm", "btn"):

            configRemove("channels", userGet(msg.from_user.id, "context_content"))
            msg.reply_text(locale("channel_removed", "msg").format(userGet(msg.from_user.id, "context_content")["name"]), reply_markup=defaultKeyboard(msg.from_user.id))
            try:
                os.remove(f"data/channels/{userGet(msg.from_user.id, 'context_content')['id']}.json")
            except FileNotFoundError:
                pass
            userClear(msg.from_user.id, "context")
            userClear(msg.from_user.id, "context_content")

    elif userGet(msg.from_user.id, "context") == "channel_ready":

        if msg.text == locale("confirm", "btn"):
            context_content = userGet(msg.from_user.id, "context_content")
            configAppend("channels", context_content)
            jsonSave(f"data/channels/{context_content['id']}.json", {"members": []})
            msg.reply_text(locale("channel_added", "msg").format(context_content["name"]), reply_markup=defaultKeyboard(msg.from_user.id))


def remindPayment(app):
    try:
        if configGet("hosted", "payment"):
            if datetime.now().day == configGet("day", "payment"):
                site_url = configGet("link", "payment").format(configGet("amount", "payment"), configGet("comment", "payment").replace(" ", "+"))
                app.send_message(
                    configGet("buyer_id"),
                    text=locale("payment", "msg").format(
                        configGet("day", "payment"),
                        configGet("amount", "payment"),
                        configGet("cardnumber", "payment")
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [InlineKeyboardButton(locale("payment_site", "clb"), url=site_url)],
                            [InlineKeyboardButton(locale("payment_direct", "clb"), callback_data="iban_payment")]
                        ]
                    )
                )
    except:
        traceback.print_exc()

if __name__ == "__main__":

    print(f'[{getDateTime(time.time())}] Starting with PID {str(pid)}')

    schedule.every().day.at("10:00").do(remindPayment, app)

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
    app.send_message(277862475, f"Starting bot with pid `{pid}`")
    #remindPayment(app)

    channels_thread = threading.Thread(target=fetch_channels, name="Channel Fetcher")
    channels_thread.start()

    idle()

    app.send_message(277862475, f"Shutting down bot with pid `{pid}`")
    print(f'\n[{getDateTime(time.time())}] Shutting down with PID {pid}')

    subprocess.call(f'kill -9 {pid}', shell=True)