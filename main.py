from bot.duck import *
from dotenv import load_dotenv
import os
import sqlite3

connection = sqlite3.connect("database.db")
c = connection.cursor()

c.execute("SELECT * FROM classes")
records = c.fetchall()
if len(records) >= 1:
    print(len(records), "classes found in table")
    # for i in records:
    #     print(i)
else:
    print("No classes in table")

# loads variables from local .env file as environment variables (use os.getenv)
load_dotenv()

duck = DuckClient()

duck.run(os.getenv("BOT_TOKEN"))
