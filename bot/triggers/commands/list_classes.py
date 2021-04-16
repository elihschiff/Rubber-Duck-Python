from . import Command
from .. import utils

import discord
import string
import json


class ListClasses(Command):
    names = ["classes", "list", "class", "roles"]
    description = "Lists all the classes and roles currently offered by the server."
    usage = "!classes or !classes [dept]"
    examples = "!classes, !classes CSCI"
    notes = "If a class isn't offered this semester, you might not be able to add it"

    names_no_courses = ["list", "roles"]
    description_no_courses = "Lists all the roles addable via the bot"
    usage = "!list"
    notes_no_courses = ""

    async def execute_command(self, client, msg, content, **kwargs):
        if not content or not client.config["ENABLE_COURSES"]:
            await self.general_listing(client, msg)
            return

        if len(content) != 4:
            await utils.delay_send(
                msg.channel, client.messages["invalid_class_list_format"]
            )
            return

        for letter in content[:4]:
            if letter not in string.ascii_letters:
                await utils.delay_send(
                    msg.channel, client.messages["invalid_class_list_format"]
                )
                return

        class_list = []

        async with client.lock:
            client.c.execute(
                "SELECT * FROM classes WHERE departments LIKE ?",
                ("%" + str(content[:4]).upper() + "%",),
            )
            records = client.c.fetchall()

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
                await utils.delay_send(msg.channel, "DMed!")

            class_str = ""
            prelude = client.messages["class_list_prelude"].format(
                str(content[:4]).upper()
            )

            delay_msg_sent = False
            for class_name in sorted(class_list):
                class_str += class_name + "\n"
                if len(class_str) + len(prelude) >= 1900:
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
        for role_category in client.roles["role_categories"]:
            roles_list = ""
            for idx, role_group in enumerate(role_category["roles"]):
                if idx > 0:
                    roles_list += utils.get_user_divider(msg.author.id) + "\n"
                for role in role_group:
                    roles_list += role["name"] + "\n"
            category_name = role_category["category_name"]
            help_name = role_category["help_name"]
            embed.add_field(
                name=f"{category_name}: `!add {help_name}`", value=roles_list
            )

        for school in client.roles["schools"]:
            dept_list = ""
            for dept in school["departments"]:
                dept_list += dept + "\n"
            school_name = school["school_name"]
            help_name = school["help_name"]
            embed.add_field(
                name=f"{category_name}: `!list {help_name}`", value=dept_list
            )

        if msg.channel.type is not discord.ChannelType.private:
            await utils.delay_send(msg.channel, "DMed!")

        await utils.delay_send(
            msg.author, client.messages["general_class_list_prelude"], embed=embed
        )

        await msg.author.send(client.messages["post_general_class_list"])
