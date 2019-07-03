from bot.duck import *
import os

duck = DuckClient()

duck.run(os.environ["BOT_TOKEN"])
