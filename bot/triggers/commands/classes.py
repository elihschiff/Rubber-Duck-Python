from . import Command
from .. import utils

import sqlite3
import discord


class Classes(Command):
    names = ["classes", "list", "class"]
    description = "Lists all the classes"
    needsContent = False

    connection = sqlite3.connect("classes.db")
    c = connection.cursor()

    async def execute_command(self, client, msg, content):
        class_list = ""
        self.c.execute("SELECT * FROM classes")
        records = self.c.fetchall()
        for i in records:
            print(i)
            class_list += "**" + i[1] + "** " + i[4] + "\n"
        embed = discord.Embed(description=class_list, color=0xDCC308)
        await utils.delay_send(msg.channel, "", embed=embed)
