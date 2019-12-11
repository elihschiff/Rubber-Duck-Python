import sys
import os
import sqlite3
import json

if len(sys.argv) < 2 or len(sys.argv) > 3 or not sys.argv[1].endswith(".db"):
    print(f"Usage: {sys.argv[0]} DB_FILE (JSON_FILE)")
    sys.exit(1)

if os.path.exists(sys.argv[1]):
    print("ERROR: database already exists... Aborting!")
    sys.exit(1)

connection = sqlite3.connect(sys.argv[1])
c = connection.cursor()

# ID is just a unique code for the table
# name is the name of the class, this is what is going to be used in discord so if you want it to be something like "DS" instead of "Data Structures" that needs to be accounted for
# channel_id is the id of the channel in discord, if this is 0 the class is not currently in discord
# course_codes is a json array as a string of the course codes. EX: ["CSCI 9999", "ITWS 8888"]
# departments is a json array as a string of the departments the course is part of. EX: ["CSCI", "ITWS"]
# identifiers is a json array as a string of the different abbreviations one might use for a class. EX: ["DS", "data struct"]
c.execute(
    """
    CREATE TABLE classes (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    channel_id INTEGER DEFAULT 0,
    course_codes TEXT NOT NULL,
    departments TEXT NOT NULL,
    identifiers TEXT NULL DEFAULT '[]',
    active INTEGER DEFAULT 1
    );
    """
)

c.execute(
    """
    CREATE TABLE emoji_users (
    user_id INTEGER DEFAULT 0
    );
    """
)

c.execute(
    """
    CREATE TABLE emoji_channels (
    channel_id INTEGER DEFAULT 0
    );
    """
)

if len(sys.argv) == 3:
    print("Updating courses in database")
    with open(sys.argv[2], "r") as courses_file:
        courses = json.load(courses_file)
        for course in courses:
            # Discord limits the length of a channel to 100 characters, therefore we keep the course name as the first 100 chars in the database so we dont have to worry about that later
            course_name_discord = course[:100].upper()

            c.execute(  # inserts the new data for a class
                """INSERT INTO classes (name, channel_id, course_codes, departments, identifiers) VALUES
                   (:name, :channel_id, :course_codes, :departments, :identifiers );""",
                {
                    "name": course_name_discord,
                    "channel_id": courses[course]["channel_id"],
                    "course_codes": str(courses[course]["course_codes"]),
                    "departments": str(courses[course]["departments"]),
                    "identifiers": str(courses[course]["identifiers"]),
                },
            )
            connection.commit()
