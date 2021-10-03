from bot.duck import *
from dotenv import load_dotenv
import os
import sqlite3
import sys

import nextcord

# set up discord intents
intents = nextcord.Intents.default()
intents.members = True

# loads variables from local .env file as environment variables (use os.getenv)
load_dotenv()

duck = DuckClient(intents)

duck.run(os.getenv("BOT_TOKEN"))
