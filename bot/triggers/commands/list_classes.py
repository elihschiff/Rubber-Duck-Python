from . import Command
from .. import utils

import sqlite3
import discord
import string
import json
import ast


class ListClasses(Command):
    names = ["classes", "list", "class"]
    description = "Lists all the classes"
    needsContent = False

    connection = sqlite3.connect("classes.db")
    c = connection.cursor()

    async def execute_command(self, client, msg, content):
        if len(content) != 4:
            await msg.channel.send(client.messages["invalid_class_list_format"])
            return

        for letter in content[:4]:
            if letter not in string.ascii_letters:
                await msg.channel.send(
                    client.messages["invalid_class_list_format"]
                )
                return

        class_list = []
        self.c.execute(
            "SELECT * FROM classes WHERE departments LIKE ?",
            ("%" + str(content[:4]).upper() + "%",),
        )
        records = self.c.fetchall()
        for i in records:
            if i[2] != 1:
                continue
            class_list.append(
                ", ".join(
                    [
                        "**" + course_code + "**"
                        for course_code in json.loads(i[4].replace("'", '"'))
                        if str(content[:4]).upper() in course_code
                    ]
                )
                + ": "
                + i[1]
            )
        if len(class_list) == 0:
            await utils.delay_send(
                msg.channel,
                client.messages["dept_not_found"].format(
                    str(content[:4]).upper()
                ),
            )
        else:
            class_str = ""
            for class_name in sorted(class_list):
                class_str += class_name + "\n"
            if msg.channel.type is discord.DMChannel:
                embed = discord.Embed(description=class_str, color=0xDCC308)
                await utils.delay_send(
                    msg.channel,
                    client.messages["class_list_prelude"].format(
                        str(content[:4]).upper()
                    ),
                    embed=embed,
                )
            else:
                await utils.delay_send(msg.channel, "DMed!")

                embed = discord.Embed(description=class_str, color=0xDCC308)
                await msg.author.send(
                    client.messages["class_list_prelude"].format(
                        str(content[:4]).upper()
                    ),
                    embed=embed,
                )
