from bot.duck import *
import os
import sqlite3
import json

connection = sqlite3.connect("classes.db")
c = connection.cursor()

# ID is just a unique code for the table
# name is the name of the class, this is what is going to be used in discord so if you want it to be something like "DS" instead of "Data Structures" that needs to be accounted for
# currently_active is if the class is active this semester, 0 inactive, 1 active
# channel_id is the id of the channel in discord, if this is 0 the class is not currently in discord
# course_codes is a json array as a string of the course codes. EX: ["CSCI 9999", "ITWS 8888"]
# departments is a json array as a string of the departments the course is part of. EX: ["CSCI", "ITWS"]
# identifiers is a json array as a string of the different abbreviations one might use for a class. EX: ["DS", "data struct"]
c.execute(
    """
    CREATE TABLE IF NOT EXISTS classes (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    currently_active INTEGER DEFAULT 0,
    channel_id INTEGER DEFAULT 0,
    course_codes TEXT NOT NULL,
    departments TEXT NOT NULL,
    identifiers TEXT NULL DEFAULT '[]'
    );"""
)

with open("config/new_courses.json", "r+") as coursesFile:
    courses = json.load(coursesFile)
    if "is_json_inserted" not in courses:
        courses["is_json_inserted"] = False

    if courses["is_json_inserted"] != True:
        courses.pop("is_json_inserted")
        # print(courses)
        for course in courses:
            # Discord limits the length of a channel to 100 characters, therefore we keep the course name as the first 100 chars in the database so we dont have to worry about that later
            courseNameDiscord = course[:100]

            # print(course)

            c.execute(  # for a specific class gets rid of the old data so we can insert the new data from the json
                """DELETE FROM classes WHERE name = :name
                """,
                {"name": courseNameDiscord},
            )
            c.execute(  # inserts the new data for a class
                """REPLACE INTO classes (name, currently_active, channel_id, course_codes, departments, identifiers) VALUES
                (:name, :currently_active, :channel_id, :course_codes, :departments, :identifiers );""",
                {
                    "name": courseNameDiscord,
                    "currently_active": courses[course]["currently_active"],
                    "channel_id": courses[course]["channel_id"],
                    "course_codes": str(courses[course]["course_codes"]),
                    "departments": str(courses[course]["departments"]),
                    "identifiers": str(courses[course]["identifiers"]),
                },
            )

        courses["is_json_inserted"] = True
        coursesFile.seek(0)
        coursesFile.write(json.dumps(courses))
        coursesFile.truncate()
        connection.commit()


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
