from bot.duck import *
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


duck = DuckClient()

bot_token = ""
with open("bot_token", "r") as token_file:
    bot_token = token_file.readline().strip()

duck.run(bot_token)
