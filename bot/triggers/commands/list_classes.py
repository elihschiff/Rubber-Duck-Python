from . import Command
from .. import utils

import discord
import string
import json
import ast


class ListClasses(Command):
    names = ["classes", "list", "class"]
    description = "Lists all the classes currently offered by the server."
    description2 = """**Description:** Lists all the classes currently offered \
    by the server. Note that if a class isn't offered this semester, you might \
    not be able to add it.
                      **Usage:** !classes or !class [dept]
                      **Examples:** !classes, !class CSCI
                      **Alternate names:** !list, !class"""
    needsContent = False

    async def execute_command(self, client, msg, content):
        if len(content) == 0:
            await self.general_listing(client, msg)
            return

        if len(content) != 4:
            await msg.channel.send(client.messages["invalid_class_list_format"])
            return

        for letter in content[:4]:
            if letter not in string.ascii_letters:
                await msg.channel.send(client.messages["invalid_class_list_format"])
                return

        class_list = []

        client.lock.acquire()
        client.c.execute(
            "SELECT * FROM classes WHERE departments LIKE ?",
            ("%" + str(content[:4]).upper() + "%",),
        )
        records = client.c.fetchall()
        client.lock.release()

        for i in records:
            class_list.append(
                ", ".join(
                    [
                        "**" + course_code + "**"
                        for course_code in json.loads(i[3].replace("'", '"'))
                        if str(content[:4]).upper() in course_code
                    ]
                )
                + ": "
                + i[1]
            )
        if len(class_list) == 0:
            await utils.delay_send(
                msg.channel,
                client.messages["dept_not_found"].format(str(content[:4]).upper()),
            )
        else:
            if msg.channel.type is not discord.ChannelType.private:
                await msg.channel.send("DMed!")

            class_str = ""
            prelude = client.messages["class_list_prelude"].format(
                str(content[:4]).upper()
            )

            delay_msg_sent = False
            for class_name in sorted(class_list):
                class_str += class_name + "\n"
                if len(class_str) + len(prelude) >= 2000:
                    embed = discord.Embed(description=class_str, color=0xDCC308)

                    await utils.delay_send(msg.author, prelude, embed=embed)
                    class_str = ""
                    delay_msg_sent = True

            if len(class_str) != 0:
                embed = discord.Embed(description=class_str, color=0xDCC308)

                if delay_msg_sent:
                    await msg.author.send(
                        client.messages["class_list_prelude"].format(
                            str(content[:4]).upper()
                        ),
                        embed=embed,
                    )
                else:
                    await utils.delay_send(
                        msg.author,
                        client.messages["class_list_prelude"].format(
                            str(content[:4]).upper()
                        ),
                        embed=embed,
                    )
                class_str = ""

    async def general_listing(self, client, msg):
        embed = discord.Embed(color=0xDCC308)
        roles_list = ""
        for role_name in client.config["general_roles"].keys():
            roles_list += role_name + "\n"
        embed.add_field(name="General Roles: `!add ROLE`", value=roles_list)

        roles_list = ""
        for role_name in client.config["major_roles"].keys():
            roles_list += role_name + "\n"
        embed.add_field(name="Major Roles: `!add MAJOR`", value=roles_list)

        for school in client.config["depts"].keys():
            school_msg = ""
            for dept in client.config["depts"][school]:
                school_msg += dept + "\n"
            school_text = school + ": `!list XXXX`"
            embed.add_field(name=school_text, value=school_msg)

        if msg.channel.type is not discord.ChannelType.private:
            await msg.channel.send("DMed!")

        await utils.delay_send(
            msg.author, client.messages["general_class_list_prelude"], embed=embed
        )

        await msg.author.send(client.messages["post_general_class_list"])
