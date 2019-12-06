import sys
import os
import sqlite3
import json

if len(sys.argv) < 2 or not sys.argv[1].endswith(".db"):
    print(f"Usage: {sys.argv[0]} DB_FILE")
    sys.exit(1)


connection = sqlite3.connect(sys.argv[1])
c = connection.cursor()

c.execute(
    """
    CREATE TABLE IF NOT EXISTS logging (
    source_channel_id INTEGER DEFAULT 0,
    dest_channel_id INTEGER DEFAULT 0
    );
    """
)


c.execute(
    """
    CREATE TABLE IF NOT EXISTS emoji_users (
    user_id INTEGER DEFAULT 0
    );
    """
)

c.execute(
    """
    CREATE TABLE IF NOT EXISTS emoji_channels (
    channel_id INTEGER DEFAULT 0
    );
    """
)

connection.commit()
