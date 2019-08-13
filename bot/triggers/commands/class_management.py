from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger

import sqlite3
import discord
import string
import json
import ast

# from fuzzyfinder import fuzzyfinder
from fuzzywuzzy import process


def fuzzy_search(c, query, max_results):
    # this matches the length of class_list but always has the name of a class corresponding
    # with the item in class_list. So if class_list has the item "DS" in slot 12 this will
    # have "Data Structures" in slot 12
    real_name_list = []
    class_list = []  # a list of ever class and every course_code etc

    c.execute("SELECT * FROM classes")
    records = c.fetchall()
    for i in records:
        if i[2] != 1:
            continue

        real_name = ", ".join(json.loads(i[4].replace("'", '"'))) + ": " + i[1]

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

    matches = process.extract(query, class_list, limit=20)
    results = []
    for match in matches:
        class_name = real_name_list[class_list.index(match[0])]
        if class_name not in results:
            results.append(class_name)
        if len(results) >= max_results:
            break

    return results


class AddClass(Command, ReactionTrigger):
    names = ["add", "join"]
    description = "Adds you to class specific channels"
    needsContent = True

    def __init__(self):
        connection = sqlite3.connect("classes.db")
        self.c = connection.cursor()

    async def execute_command(self, client, msg, content):
        options = fuzzy_search(self.c, content, 5)

        await utils.generate_react_menu(
            msg,
            msg.author.id,
            client.messages["add_class_prompt"].format(content),
            5,
            options,
            "No results match",
        )

    async def execute_reaction(self, client, reaction, user):
        if user.bot:
            return

        msg = reaction.message
        if msg.author != client.user:
            return

        if user not in msg.mentions:
            return

        if (
            reaction.emoji not in utils.emoji_numbers
            and reaction.emoji != utils.no_matching_results_emote
        ):
            return

        if " add " not in msg.content:
            return

        line_start_idx = msg.content.index(reaction.emoji)
        start_idx = msg.content.index(":", line_start_idx) + 1
        end_idx = msg.content.index("\n", line_start_idx)

        await msg.clear_reactions()

        course_name = msg.content[start_idx:end_idx].strip()
        self.c.execute(f"SELECT * FROM classes WHERE name = '{course_name}'")
        course = self.c.fetchone()
        print(course)
        channel_id = int(course[3])

        channel = None
        if channel_id != 0:
            channel = client.get_channel(channel_id)
        else:
            new_channel_name = (
                course_name[:100].strip().replace(" ", "-").lower()
            )

            class_category_channel = client.get_channel(
                client.config["CLASS_CATEGORY_ID"]
            )

            all_seer = client.SERVER.get_role(client.config["ALL_SEER_ID"])
            time_out = client.SERVER.get_role(client.config["TIME_OUT_ID"])

            # ensure alphabetical ordering
            insert_idx = len(class_category_channel.text_channels) + 1
            for channel in class_category_channel.text_channels:
                insert_idx = channel.position - 1
                if channel.name > new_channel_name:
                    break

            try:
                channel = await class_category_channel.create_text_channel(
                    new_channel_name,
                    position=insert_idx,
                    topic=", ".join(json.loads(course[4].replace("'", '"')))
                    + ": "
                    + course[1],
                    overwrites={
                        client.SERVER.default_role: discord.PermissionOverwrite(
                            read_messages=False
                        ),
                        all_seer: discord.PermissionOverwrite(
                            read_messages=True
                        ),
                        time_out: discord.PermissionOverwrite(
                            send_messages=False, add_reactions=False
                        ),
                    },
                )
            except HttpException:
                msg.channel.send(client.messages["err_too_many_channels"])
                return

            self.c.execute(
                f"UPDATE classes SET channel_id = {channel.id} WHERE name = '{course_name}'"
            )

        overwrite = discord.PermissionOverwrite()
        overwrite.read_messages = True
        await channel.set_permissions(user, overwrite=overwrite)

        await utils.delay_send(
            msg.channel,
            client.messages["class_add_confirmation"].format(course_name),
        )


class RemoveClass(Command, ReactionTrigger):
    names = ["remove", "leave"]
    description = "Removes you from class specific channels"
    needsContent = True

    def __init__(self):
        connection = sqlite3.connect("classes.db")
        self.c = connection.cursor()

    async def execute_command(self, client, msg, content):
        options = fuzzy_search(self.c, content, 5)

        await utils.generate_react_menu(
            msg,
            msg.author.id,
            client.messages["remove_class_prompt"].format(content),
            5,
            options,
            "No results match",
        )

    async def execute_reaction(self, client, reaction, user):
        if user.bot:
            return

        msg = reaction.message
        if msg.author != client.user:
            return

        if user not in msg.mentions:
            return

        if (
            reaction.emoji not in utils.emoji_numbers
            and reaction.emoji != utils.no_matching_results_emote
        ):
            return

        if " remove " not in msg.content:
            return

        line_start_idx = msg.content.index(reaction.emoji)
        start_idx = msg.content.index(":", line_start_idx) + 1
        end_idx = msg.content.index("\n", line_start_idx)

        await msg.clear_reactions()

        course_name = msg.content[start_idx:end_idx].strip()
        self.c.execute(f"SELECT * FROM classes WHERE name = '{course_name}'")
        print(self.c.fetchone())
        return
        channel_id = int(self.c.fetchone()[3])

        print(channel_id)

        if channel_id != 0:
            channel = client.get_channel(channel_id)

            await channel.set_permissions(user, overwrite=None)

        await msg.channel.send(
            client.messages["class_remove_confirmation"].format(course_name)
        )
