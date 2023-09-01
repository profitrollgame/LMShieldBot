## Synapse

This bot reminds you to update the shield after the provided time.
It **does not** connect to the game in any way.

### Requirements
* Python 3.7+
* Pyrogram
* TgCrypto
* ujson

### Quickstart
1. `git clone https://github.com/profitrollgame/LMShieldBot`
2. `cd ./LMShieldBot`
3. `python -m venv .venv`
4. `source .venv/bin/activate`
5. `pip install -r requirements.txt`
6. `cp config_example.ini config.ini`
7. `cp config_example.json config.json`
8. Set up `config.ini` and `config.json` using any text editor (example: `nano config.json`)
9. `python shieldbot.py`
  
### Where to find values for configs
* For `config.ini` api creds are found [here](https://my.telegram.org/apps), bot token must be from [@BotFather](https://t.me/BotFather);
* For `config.json` userid can be found using [this bot](https://t.me/userinfobot).
