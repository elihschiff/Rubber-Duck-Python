from bot.duck import *
from bot.triggers import load_cogs
from dotenv import load_dotenv
import os

# loads variables from local .env file as environment variables (use os.getenv)
load_dotenv()

duck = DuckClient()

load_cogs(duck)

duck.run(os.getenv("BOT_TOKEN"))
