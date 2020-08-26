import requests
import sys
import sqlite3
import json

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print(f"USAGE: python {sys.argv[0]} DB_NAME [IDENTIFIERS]")
    sys.exit(1)


# Uncomment next line to use current yacs data
# raw_course_data = requests.get("https://yacs.cs.rpi.edu/api/v6/listings").json()


# Uncomment next section to use data scraped from quacs
with open("quacs-data/courses.json") as f:
    quacs_data = json.load(f)
# End quacs data section


courses = {}

for dept in quacs_data:
    for course in dept["courses"]:
        # the following line removes extra spaces from the course name
        # and capitalizes it.
        course_name = " ".join(course["name"].split()).upper()
        course_dept = course["subj"]
        course_code = f"{course['subj']} {course['crse']}"

        print(f"Parsing course: {course_name}")

        if int(course["csre"]) >= 6000:
            continue

        if course_name in courses:
            courses[course_name]["course_codes"].append(course_code)
            courses[course_name]["departments"].append(course_dept)
        else:
            courses[course_name] = {
                "course_codes": [course_code],
                "departments": [course_dept],
                "identifiers": [],
            }

if len(sys.argv) == 3:
    course_identifiers = {}
    with open(sys.argv[2], "r") as identifiers_file:
        course_identifiers = json.load(identifiers_file)
    for course, identifiers in course_identifiers.items():
        if course in courses:
            print(f"Loading identifiers for: {course}")
            courses[course]["identifiers"] = identifiers

connection = sqlite3.connect(sys.argv[1])
c = connection.cursor()

for course_name, course in courses.items():
    course_name_discord = course_name[:100]

    c.execute("SELECT * FROM classes WHERE name = :name", {"name": course_name_discord})
    if not c.fetchall():
        # course is not in the database, so insert it
        c.execute(
            """INSERT INTO classes (name, course_codes, departments, identifiers)
                   VALUES (:name, :course_codes, :departments, :identifiers);""",
            {
                "name": course_name_discord,
                "course_codes": str(course["course_codes"]),
                "departments": str(course["departments"]),
                "identifiers": str(course["identifiers"]),
            },
        )
    else:
        # course is in the database, so just update it
        c.execute(
            "UPDATE classes SET course_codes = :course_codes, departments = :departments WHERE name = :name;",
            {
                "name": course_name_discord,
                "course_codes": str(course["course_codes"]),
                "departments": str(course["departments"]),
            },
        )
    connection.commit()
