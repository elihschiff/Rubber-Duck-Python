import requests
import sys
import sqlite3
from dotenv import load_dotenv
import os
import json

if len(sys.argv) != 3:
    print(f"USAGE: python {sys.argv[0]} QUACS_DATA DB_NAME")
    sys.exit(1)

with open(sys.argv[1]) as f:
    quacs_data = json.load(f)

# Load data
raw_course_data = []
for department in quacs_data:
    for course in department["courses"]:
        course_data = {}
        course_data["title"] = course["title"]
        course_data["crse"] = course["crse"]
        course_data["dept"] = department["code"].upper()
        raw_course_data.append(course_data)

# Parse raw data into something easier to use
courses = []
for course in raw_course_data:
    # the following line removes extra spaces from the course name
    # and capitalizes it.
    course_name = " ".join(course["title"].split()).upper()
    if int(course["crse"]) < 6000:
        courses.append(
            {
                "name": course_name[:100],
                "code": f'{course["dept"]} {course["crse"]}',
                "dept": course["dept"],
            }
        )

connection = sqlite3.connect(sys.argv[2])
c = connection.cursor()

# Set all courses to inactive
c.execute("UPDATE classes SET active = 0;")

# Update courses which already existed
for course in courses:
    c.execute(
        "UPDATE classes SET active = 1 WHERE name = :name OR instr(course_codes, :code);",
        course,
    )

# Identify new courses (their name and course code is different)
new_courses = []
for course in courses:
    c.execute(
        "SELECT * FROM classes WHERE name = :name OR instr(course_codes, :code);",
        course,
    )
    if c.fetchone() is None:
        new_courses.append(course)

# Add new courses
for course in new_courses:
    c.execute(
        "INSERT INTO classes (name, course_codes, departments, active) VALUES (:name, :course_codes, :departments, 1);",
        {
            "name": course["name"],
            "course_codes": json.dumps([course["code"]]),
            "departments": json.dumps([course["dept"]]),
        },
    )

# Display changes and prompt for confirmation
print("Inactive courses:")
c.execute("SELECT name FROM classes WHERE active = 0;")
for course in c.fetchall():
    print(f"\t{course[0]}")

print("\nActive courses:")
c.execute("SELECT name FROM classes WHERE active = 1;")
for course in c.fetchall():
    print(f"\t{course[0]}")

res = ""
while res not in ("yes", "no"):
    try:
        res = input("Type 'yes' to confirm these changes or 'no' to exit")
    except EOFError:
        break

    if res == "yes":
        connection.commit()
