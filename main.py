from bot.duck import *
import os
import sqlite3

connection = sqlite3.connect("classes.db")
c = connection.cursor()

# course-codes must be a string in the format "CSCI-1200 MATH-2010" so department followed by dash followed by number and a space between them
#  departments must be a string in the format "CSCI MATH" with no repeats
# identifiers must be a string in the format "DS, data struct" where each identifier is separated by a string
c.execute(
    """
    CREATE TABLE IF NOT EXISTS classes (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    active INTEGER,
    channel_id INTEGER,
    course_codes TEXT NOT NULL,
    departments TEXT NOT NULL,
    identifiers TEXT NULL DEFAULT ''
    );"""
)

# c.execute(
#     """INSERT INTO classes (name, active, channel_id, course_codes, departments, identifiers) VALUES
#     (
#     "data structures",
#     0,
#     0,
#     "CSCI-1200",
#     "CSCI",
#     "DS, data struct"
#     );
#     """
# )
# connection.commit()

c.execute("SELECT * FROM classes")
records = c.fetchall()
if len(records) >= 1:
    print("Classes found in table")
    for i in records:
        print(i)
else:
    print("No classes in table")

duck = DuckClient()

bot_token = ""
with open("bot_token", "r") as token_file:
    bot_token = token_file.readline().strip()

duck.run(bot_token)
