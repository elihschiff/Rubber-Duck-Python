import sys
import os
import sqlite3
import json

if len(sys.argv) != 2 or not sys.argv[1].endswith(".db"):
    print(f"Usage: {sys.argv[0]} DB_FILE")
    sys.exit(1)

if os.path.exists(sys.argv[1]):
    print("ERROR: database already exists... Aborting!")
    sys.exit(1)

connection = sqlite3.connect(sys.argv[1])
c = connection.cursor()

c.execute(
    """
    CREATE TABLE logging (
    source_channel_id INTEGER DEFAULT 0,
    dest_channel_id INTEGER DEFAULT 0
    );
    """
)

c.execute(
    """
    CREATE TABLE unused_logging (
    channel_id INTEGER DEFAULT 0
    );
    """
)

connection.commit()
