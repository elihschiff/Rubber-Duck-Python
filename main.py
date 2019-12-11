from bot.duck import *
from dotenv import load_dotenv
import os

# loads variables from local .env file as environment variables (use os.getenv)
load_dotenv()

duck = DuckClient()

duck.run(os.getenv("BOT_TOKEN"))
