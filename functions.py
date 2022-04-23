from datetime import datetime
import gzip
import os
import shutil
import time
import json

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup


def getDateTime(timestamp):
    return time.strftime("%H:%M:%S | %d.%m.%Y", time.localtime(int(timestamp)))


def jsonSave(filename, value):
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(value, f, indent=4, ensure_ascii=False)
        f.close()

def jsonLoad(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        value = json.load(f)
        f.close()
    return value


def locale(key: str, *args: str):
    strings = jsonLoad("strings.json")
    string = strings
    for dict_key in args:
        string = string[dict_key]
    return string[key]

def configGet(key: str, *args: str):
    this_dict = jsonLoad("config.json")
    this_key = this_dict
    for dict_key in args:
        this_key = this_key[dict_key]
    return this_key[key]

def configAppend(key: str, value):
    config = jsonLoad("config.json")
    config[key].append(value)
    jsonSave("config.json", config)

def configRemove(key: str, value):
    config = jsonLoad("config.json")
    config[key].remove(value)
    jsonSave("config.json", config)

def defaultKeyboard():
    return ReplyKeyboardMarkup(
        [
            [locale("shield_4h", "btn"), locale("shield_8h", "btn"), locale("shield_24h", "btn")],
            [locale("shield_3d", "btn"), locale("shield_7d", "btn"), locale("shield_14d", "btn")],
            [locale("shield_reset", "btn")]
        ],
        resize_keyboard=True
    )

def checkSize():
    
    i = 0

    while i < 2:
        try:
            log = os.stat('logs/latest.log')

            if (log.st_size / 1024) > 1024:
                with open('logs/latest.log', 'rb', encoding='utf-8') as f_in:
                    with gzip.open(f'logs/{datetime.now().strftime("%d.%m.%Y_%H:%M:%S")}.zip', 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                            
                open('logs/latest.log', 'w', encoding='utf-8').close()
                
            i = 2

        except FileNotFoundError:
            
            try:
                log = open('logs/latest.log', 'a', encoding='utf-8')
                open('logs/latest.log', 'a', encoding='utf-8').close()
            except:
                try:
                    os.mkdir('logs')
                    log = open('logs/latest.log', 'a', encoding='utf-8')
                    open('logs/latest.log', 'a', encoding='utf-8').close()
                except:
                    pass
            
            i += 1


def appendLog(message):
    global logs_folder

    checkSize()

    try:
        log = open('logs/latest.log', 'a', encoding='utf-8')
        open('logs/latest.log', 'a').close()
    except:
        try:
            os.mkdir('logs')
            log = open('logs/latest.log', 'a', encoding='utf-8')
            open('logs/latest.log', 'a').close()
        except:
            time.sleep(2)
            print('Log file could not be created')
            return
            
    log.write(f'[{getDateTime(datetime.now().timestamp)}] {message}\n')
    log.close()


def gotExp(app, traceback, exc_info, exp, funcname, command="No command", userstr=["Unknown", 000]):

    exception_type, exception_object, exception_traceback = exc_info
    filename = exception_traceback.tb_frame.f_code.co_filename
    line_number = exception_traceback.tb_lineno

    appendLog(f"Exception caught: {exp} (type: {str(exception_type)}, filename: {filename} on line {str(line_number)}) Full exception:\n{traceback.format_exc()}")

    error_msg = f'Exception caught:\n\nName: `{exp}`\nCommand: {str(command)}\nUser: `{userstr[0]}` (`{str(userstr[1])}`)\nFile: `{filename}` on line `{str(line_number)}`\n\nTraceback:\n```{traceback.format_exc()}```'

    app.send_message(configGet("ownerid"), error_msg)

    traceback.print_exc()