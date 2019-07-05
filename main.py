from bot.duck import *
import os

duck = DuckClient()

bot_token = ""
with open("bot_token", "r") as token_file:
    bot_token = token_file.readline().strip()

duck.run(bot_token)
