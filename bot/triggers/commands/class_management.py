from . import Command
from .. import utils

import sqlite3
import discord
import string
import json
import ast

# from fuzzyfinder import fuzzyfinder
from fuzzywuzzy import process


class AddClass(Command):
    names = ["add", "search"]
    description = "Adds you to hidden class specific channels"
    needsContent = True

    connection = sqlite3.connect("classes.db")
    c = connection.cursor()

    async def execute_command(self, client, msg, content):
        # this matches the length of class_list but always has the name of a class corresponding with the item in class_list. So if class_list has the item "DS" in slot 12 this will have "Data Structures" in slot 12
        real_name_list = []
        class_list = []  # a list of ever class and every course_code etc

        self.c.execute("SELECT * FROM classes")
        records = self.c.fetchall()
        for i in records:
            if i[2] != 1:
                continue

            real_name = (
                i[1] + "     " + ", ".join(json.loads(i[4].replace("'", '"')))
            )

            class_list.append(i[1])
            real_name_list.append(real_name)

            codes = json.loads(i[4].replace("'", '"'))
            for code in codes:
                class_list.append(code)
                real_name_list.append(real_name)

            identifiers = json.loads(i[6].replace("'", '"'))
            for ident in identifiers:
                class_list.append(ident)
                real_name_list.append(real_name)

        matches = process.extract(content, class_list, limit=20)
        print(matches)
        options = []
        for match in matches:
            class_name = real_name_list[class_list.index(match[0])]
            if class_name not in options:
                options.append(class_name)
            if len(options) >= 5:
                break

        await utils.generate_react_menu(
            msg,
            msg.author.id,
            f", You search for **{content}** here are the results.\nClick the corresponding reaction to add that class:",
            5,
            options,
            "No results match",
        )


class ListClasses(Command):
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
