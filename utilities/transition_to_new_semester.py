import requests
import sys
import sqlite3
import discord
from dotenv import load_dotenv
import os
import json

if len(sys.argv) != 3:
    print(f"USAGE: python {sys.argv[0]} QUACS_DATA DB_NAME")
    sys.exit(1)


# Uncomment next line to use current yacs data
# raw_course_data = requests.get("https://yacs.cs.rpi.edu/api/v6/listings").json()


# Uncomment next section to use data scraped from quacs
with open(sys.argv[1]) as f:
    quacs_data = json.load(f)

raw_course_data = {}
raw_course_data["data"] = []
for department in quacs_data:
    for course in department["courses"]:
        course_data = {}
        course_data["attributes"] = {}
        course_data["attributes"]["title"] = course["title"]
        course_data["attributes"]["crse"] = course["crse"]
        raw_course_data["data"].append(course_data)
# End quacs data section


courses = set()

for course in raw_course_data["data"]:
    # the following line removes extra spaces from the course name
    # and capitalizes it.
    course_name = " ".join(course["attributes"]["title"].split()).upper()
    print(f"Parsing course: {course_name}")
    if int(course["attributes"]["crse"]) < 6000:
        courses.add(course_name)

connection = sqlite3.connect(sys.argv[2])
c = connection.cursor()

c.execute("UPDATE classes SET active = 0;")

for course in courses:
    course_name_discord = course[:100]

    c.execute(
        "UPDATE classes SET active = 1 WHERE name = :name;",
        {"name": course_name_discord},
    )

connection.commit()

bot = discord.Client()


@bot.event
async def on_ready():
    c.execute("SELECT channel_id FROM classes WHERE active = 0 AND channel_id != 0;")
    for channel_id in c.fetchall():
        print(f"Hiding {channel_id[0]}")
        await bot.get_channel(channel_id[0]).edit(sync_permissions=True)
    sys.exit(0)


load_dotenv()
bot.run(os.getenv("BOT_TOKEN"))
