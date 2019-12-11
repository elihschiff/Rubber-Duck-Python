import sys
import sqlite3
import json

if len(sys.argv) < 2 or len(sys.argv) > 3:
    print(
        f"USAGE: python {sys.argv[0]} DB_NAME [OUTFILE (defaults to identifiers.json)]"
    )
    sys.exit(1)

identifiers = {}

connection = sqlite3.connect(sys.argv[1])
c = connection.cursor()

c.execute('SELECT * FROM classes WHERE identifiers != "[]"')

for course in c.fetchall():
    course_name = course[1]
    course_identifiers = course[5]
    identifiers[course_name] = course_identifiers

out_fname = "identifiers.json"
if len(sys.argv) == 3:
    out_fname = sys.argv[2]

with open(out_fname, "w") as f:
    json.dump(identifiers, f)
