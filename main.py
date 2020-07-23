import os
import sys

from dotenv import load_dotenv

from bot.duck import DuckClient

# loads variables from local .env file as environment variables (use os.getenv)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("ERROR: NO TOKEN PROVIDED.  ABORTING...")
    sys.exit(1)

DUCK = DuckClient()

DUCK.run(BOT_TOKEN)
