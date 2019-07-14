from . import Command
from .. import utils

import sqlite3
import discord
import string
import json
import ast


class Classes(Command):
    names = ["classes", "list", "class"]
    description = "Lists all the classes"
    needsContent = True

    connection = sqlite3.connect("classes.db")
    c = connection.cursor()

    async def execute_command(self, client, msg, content):
        for letter in content[:4]:
            if letter not in string.ascii_letters:
                await utils.delay_send(
                    msg.channel,
                    "This command needs to be of the form !classes followed by 4 letters example: `!classes csci`",
                )
                return
        class_list = ""
        self.c.execute(
            "SELECT * FROM classes WHERE departments LIKE ?",
            ("%" + str(content[:4]).upper() + "%",),
        )
        records = self.c.fetchall()
        for i in records:
            if i[2] != 1:
                continue
            codes = i[4][2 : len(i[4]) - 2]
            codes = codes.replace("', '", " ")
            class_list += "**" + i[1] + "** "
            # class_list += codes
            class_list += "\n"
        if len(class_list) == 0:
            await utils.delay_send(
                msg.channel,
                f"I am sorry I could not find a class from the department `{str(content[:4]).upper()}` if you want an easy list of the 4 letter department codes check out <http://yacs.cs.rpi.edu/>",
            )
        else:
            embed = discord.Embed(description=class_list, color=0xDCC308)
            await utils.delay_send(msg.channel, "", embed=embed)
