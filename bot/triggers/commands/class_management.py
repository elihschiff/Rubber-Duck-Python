from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger

import discord
import string
import json
import ast
import re

# from fuzzyfinder import fuzzyfinder
from fuzzywuzzy import process


async def fuzzy_search(client, query, max_results):
    # this matches the length of class_list but always has the name of a class corresponding
    # with the item in class_list. So if class_list has the item "DS" in slot 12 this will
    # have "Data Structures" in slot 12
    real_name_list = []
    class_list = []  # a list of ever class and every course_code etc

    async with client.lock:
        client.c.execute("SELECT * FROM classes WHERE active != 0")
        records = client.c.fetchall()

    for i in records:
        real_name = "**" + ", ".join(json.loads(i[3].replace("'", '"'))) + "**: " + i[1]

        class_list.append(i[1])
        real_name_list.append(real_name)

        codes = json.loads(i[3].replace("'", '"'))
        for code in codes:
            class_list.append(code)
            real_name_list.append(real_name)

        identifiers = json.loads(i[5].replace("'", '"'))
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


async def add_role(client, msg, role_id, role_name):
    role = client.SERVER.get_role(role_id)
    server_member = client.SERVER.get_member(msg.author.id)
    await server_member.add_roles(role)

    if role_name == "-------":
        await msg.author.send(client.messages["add_hidden_role"])
        if msg.channel.type is not discord.ChannelType.private:
            await utils.delay_send(
                msg.channel, client.messages["add_hidden_role_public"]
            )
    elif role_name:
        await utils.delay_send(
            msg.channel, client.messages["add_role_confirmation"].format(role_name)
        )


async def remove_role(client, msg, role_id, role_name):
    role = client.SERVER.get_role(role_id)
    server_member = client.SERVER.get_member(msg.author.id)
    await server_member.remove_roles(role)

    if role_name == "-------":
        await msg.author.send(client.messages["remove_hidden_role"])
        if msg.channel.type is not discord.ChannelType.private:
            await utils.delay_send(
                msg.channel, client.messages["remove_hidden_role_public"]
            )
    elif role_name:
        await utils.delay_send(
            msg.channel, client.messages["remove_role_confirmation"].format(role_name)
        )


class AddClass(Command, ReactionTrigger):
    names = ["add", "join", "register"]
    description = "Adds you to roles and class specific channels"
    usage = "!add [class code]"
    examples = f"!add cs1200, !add Computer Science"
    notes = f"To see available roles, majors, and classes, use !list"

    names_no_courses = ["add", "join", "addrole", "joinrole"]
    description_no_courses = "Adds you to a role"
    usage_no_courses = "!add [role]"
    examples = f"!add Computer Science"
    notes_no_courses = f"To see available roles, use !list"

    def __init__(self):
        self.alphanum_re = re.compile("[^\w ]+")

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, client.messages["add_no_content"])
            return

        if content == "%":
            await utils.delay_send(msg.channel, client.messages["add_mod_message"])
            return

        for word in client.config["add_skip_words"]:
            if content.split()[0].lower() == word.lower():
                content = " ".join(content.split()[1:]).strip()
                break

        if not content:
            await utils.delay_send(
                msg.channel, client.messages["invalid_class_add_format"]
            )
            return

        for role_category in client.roles["role_categories"]:
            for role in role_category["roles"]:
                if content.lower() == role["name"].lower() or any(
                    [
                        content.lower() == alt_name.lower()
                        for alt_name in role["alternate_names"]
                    ]
                ):
                    await add_role(client, msg, role["id"], role["name"])
                    if role["id"] == client.config["all_seer_id"]:
                        await remove_role(
                            client, msg, client.config["non_all_seer_id"], None
                        )
                    return

        if not client.config["ENABLE_COURSES"]:
            await utils.delay_send(msg.channel, client.messages["add_no_roles_match"])
            return

        options = await fuzzy_search(client, content, 5)

        if msg.channel.type is not discord.ChannelType.private:
            await utils.delay_send(msg.channel, "DMed!")

        await utils.generate_react_menu(
            msg.author,
            msg.author.id,
            client.messages["add_class_prompt"].format(content),
            5,
            options,
            "No results match",
        )

    # a temp var that is ok to reset on reboot.
    # It keeps a list of people and classes that were recently added to reduce welcome message spam
    recent_class_cache = []

    async def execute_reaction(self, client, reaction, channel, msg, user):
        if not client.config["ENABLE_COURSES"]:
            return

        # user = await client.fetch_user(reaction.user_id)
        if user.bot:
            return

        # channel = await client.fetch_channel(reaction.channel_id)
        if channel.type is not discord.ChannelType.private:
            return

        # msg = await channel.fetch_message(reaction.message_id)
        if msg.author != client.user:
            return

        if user not in msg.mentions:
            return

        if " add " not in msg.content:
            return

        if reaction.emoji.name == utils.no_matching_results_emote:
            await utils.delay_send(msg.channel, client.messages["add_no_roles_match"])

        if reaction.emoji.name not in utils.emoji_numbers:
            return

        line_start_idx = msg.content.index(reaction.emoji.name)
        start_idx = msg.content.index(":", line_start_idx) + 1
        end_idx = msg.content.index("\n", line_start_idx)

        course_name = msg.content[start_idx:end_idx].strip()
        async with client.lock:
            client.c.execute(
                "SELECT * FROM classes WHERE name = :course_name",
                {"course_name": course_name},
            )
            course = client.c.fetchone()
            channel_id = int(course[2])

        channel = None
        if channel_id != 0:
            channel = client.get_channel(channel_id)
        else:
            course_name = " ".join(course_name.replace("/", " ").split())
            new_channel_name = self.alphanum_re.sub(" ", course_name.lower())
            new_channel_name = " ".join(new_channel_name.split()).replace(" ", "-")

            added = False
            for category_id in client.config["class_category_ids"]:
                class_category_channel = client.get_channel(category_id)

                all_seer = client.SERVER.get_role(client.config["all_seer_id"])
                time_out = client.SERVER.get_role(client.config["time_out_id"])

                try:
                    channel = await class_category_channel.create_text_channel(
                        new_channel_name,
                        topic=", ".join(json.loads(course[3].replace("'", '"')))
                        + ": "
                        + course[1],
                        overwrites={
                            client.SERVER.default_role: discord.PermissionOverwrite(
                                read_messages=False
                            ),
                            all_seer: discord.PermissionOverwrite(read_messages=True),
                            time_out: discord.PermissionOverwrite(
                                send_messages=False, add_reactions=False
                            ),
                        },
                    )
                    added = True
                except discord.HTTPException as e:
                    continue

                async with client.lock:
                    client.c.execute(
                        "UPDATE classes SET channel_id = :channel_id WHERE name = :course_name",
                        {"channel_id": channel.id, "course_name": course_name},
                    )
                    client.connection.commit()

                break

            if not added:
                await utils.delay_send.send(
                    msg.channel,
                    "Error: Unable to add course.  Please message an admin about this.",
                )
                return

        try:
            overwrite = discord.PermissionOverwrite()
            overwrite.read_messages = True
            await channel.set_permissions(user, overwrite=overwrite)

            await utils.delay_send(
                msg.channel,
                client.messages["class_add_confirmation"].format(course_name),
            )

            # check if this user and channel is in the cache
            for past_user, past_channel in self.recent_class_cache:
                if past_user == user.id and past_channel == channel.id:
                    return

            self.recent_class_cache.append((user.id, channel.id))
            if len(self.recent_class_cache) > client.config["recent_class_cache_size"]:
                self.recent_class_cache.pop(0)

            await utils.delay_send(
                channel,
                client.messages["class_add_welcome"].format(course_name, user.mention),
            )

        except Exception as e:
            await utils.delay_send(
                msg.channel, client.messages["err_adding_class"].format(e)
            )
            await utils.sendTraceback(client, msg.content)


class RemoveClass(Command, ReactionTrigger):
    names = ["remove", "leave", "sub", "unregister", "drop"]
    description = "Removes you from roles and class specific channels"
    usage = "!remove [class code]"
    examples = f"!remove Bio 1010, !remove Chemistry"

    names_no_courses = ["remove", "leave", "leaverole", "drop", "droprole"]
    description_no_courses = "Removes you from a role"
    usage_no_courses = "!remove [role]"
    examples = f"!remove Chemistry"

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, client.messages["remove_no_content"])
            return

        for word in client.config["add_skip_words"]:
            if content.split()[0].lower() == word.lower():
                content = " ".join(content.split()[1:]).strip()
                break

        for role_category in client.roles["role_categories"]:
            for role in role_category["roles"]:
                if content.lower() == role["name"].lower() or any(
                    [
                        content.lower() == alt_name.lower()
                        for alt_name in role["alternate_names"]
                    ]
                ):
                    await remove_role(client, msg, role["id"], role["name"])
                    if role["id"] == client.config["all_seer_id"]:
                        await add_role(
                            client, msg, client.config["non_all_seer_id"], None
                        )
                    return

        if not client.config["ENABLE_COURSES"]:
            await utils.delay_send(
                msg.channel, client.messages["remove_no_roles_match"]
            )
            return

        options = await fuzzy_search(client, content, 5)

        if msg.channel.type is not discord.ChannelType.private:
            await utils.delay_send(msg.channel, "DMed!")

        await utils.generate_react_menu(
            msg.author,
            msg.author.id,
            client.messages["remove_class_prompt"].format(content),
            5,
            options,
            "No results match",
        )

    async def execute_reaction(self, client, reaction, channel, msg, user):
        if not client.config["ENABLE_COURSES"]:
            return

        # user = await client.fetch_user(reaction.user_id)
        if user.bot:
            return

        # channel = await client.fetch_channel(reaction.channel_id)
        if channel.type is not discord.ChannelType.private:
            return

        # msg = await channel.fetch_message(reaction.message_id)
        if msg.author != client.user:
            return

        if user not in msg.mentions:
            return

        if " remove " not in msg.content:
            return

        if reaction.emoji.name == utils.no_matching_results_emote:
            await utils.delay_send(
                msg.channel, client.messages["remove_no_roles_match"]
            )

        if reaction.emoji.name not in utils.emoji_numbers:
            return

        line_start_idx = msg.content.index(reaction.emoji.name)
        start_idx = msg.content.index(":", line_start_idx) + 1
        end_idx = msg.content.index("\n", line_start_idx)

        course_name = msg.content[start_idx:end_idx].strip()
        async with client.lock:
            client.c.execute(
                f"SELECT channel_id FROM classes WHERE name = '{course_name}'"
            )
            channel_id = int(client.c.fetchone()[0])

        try:
            if channel_id != 0:
                channel = client.get_channel(channel_id)

                await channel.set_permissions(user, overwrite=None)

            await utils.delay_send(
                msg.channel,
                client.messages["class_remove_confirmation"].format(course_name),
            )
        except Exception as e:
            await utils.delay_send(
                msg.channel, client.messages["err_removing_class"].format(e)
            )
            await utils.sendTraceback(client, msg.content)
