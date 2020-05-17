import json
import re
from typing import Any, cast, List, Tuple, Optional

from fuzzywuzzy import process

import discord

from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger
from ...duck import DuckClient

ALPHANUM_RE = re.compile(r"[^\w ]+")

# Cache of users who recently added a class.  Used to avoid spamming class
# channels with add messages if they re-add the class repeatedly.
# This will be reset when the bot reboots, but that's not too bad.
RECENTLY_ADDED_CACHE: List[Tuple[int, int]] = []


async def get_course_channel(
    client: DuckClient, msg_content: str, emoji: str
) -> Tuple[str, Optional[discord.TextChannel]]:
    course, course_name, channel_id = get_course(client, msg_content, emoji)

    if channel_id != 0:
        return course_name, cast(discord.TextChannel, client.get_channel(channel_id))

    course_name = " ".join(course_name.replace("/", " ").split())
    new_channel_name = ALPHANUM_RE.sub(" ", course_name.lower())
    new_channel_name = " ".join(new_channel_name.split()).replace(" ", "-")

    for category_id in client.config["class_category_ids"]:
        channel = await try_generate_course_channel(
            client, category_id, course, course_name, new_channel_name
        )
        if channel:
            return course_name, channel
    return course_name, None


async def try_generate_course_channel(
    client: DuckClient,
    category_id: int,
    course: List[str],
    course_name: str,
    channel_name: str,
) -> Optional[discord.TextChannel]:
    class_category_channel = client.get_channel(category_id)
    class_category_channel = cast(discord.CategoryChannel, class_category_channel)

    all_seer = client.server.get_role(client.config["all_seer_id"])
    time_out = client.server.get_role(client.config["time_out_id"])

    try:
        channel = await class_category_channel.create_text_channel(
            channel_name,
            topic=", ".join(json.loads(course[3].replace("'", '"'))) + ": " + course[1],
            overwrites={
                client.server.default_role: discord.PermissionOverwrite(
                    read_messages=False
                ),
                all_seer: discord.PermissionOverwrite(read_messages=True),  # type: ignore
                time_out: discord.PermissionOverwrite(  # type: ignore
                    send_messages=False, add_reactions=False
                ),
            },
        )
    except discord.HTTPException:
        return None

    client.cursor.execute(
        "UPDATE classes SET channel_id = :channel_id WHERE name = :course_name",
        {"channel_id": channel.id, "course_name": course_name},
    )
    client.connection.commit()

    return channel


def get_course(
    client: DuckClient, msg_content: str, emoji: str
) -> Tuple[Any, str, int]:
    line_start_idx = msg_content.index(emoji)
    start_idx = msg_content.index(":", line_start_idx) + 1
    end_idx = msg_content.index("\n", line_start_idx)

    course_name = msg_content[start_idx:end_idx].strip()
    client.cursor.execute(
        "SELECT * FROM classes WHERE name = :course_name", {"course_name": course_name},
    )
    course = client.cursor.fetchone()
    return course, course_name, int(course[2])


def get_class_list(client: DuckClient) -> Tuple[List[str], List[str]]:
    real_name_list = []
    class_list = []  # a list of ever class and every course_code etc

    client.cursor.execute("SELECT * FROM classes WHERE active != 0")
    records = client.cursor.fetchall()

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

    return real_name_list, class_list


async def fuzzy_search(client: DuckClient, query: str, max_results: int) -> List[str]:
    # this matches the length of class_list but always has the name of a class corresponding
    # with the item in class_list. So if class_list has the item "DS" in slot 12 this will
    # have "Data Structures" in slot 12

    real_name_list, class_list = get_class_list(client)

    matches = process.extract(query, class_list, limit=20)
    results = []
    for match in matches:
        class_name = real_name_list[class_list.index(match[0])]
        if class_name not in results:
            results.append(class_name)
        if len(results) >= max_results:
            break

    return results


async def add_role(
    client: DuckClient, msg: discord.Message, role_id: int, role_name: str
) -> None:
    role = client.server.get_role(role_id)
    role = cast(discord.Role, role)

    server_member = client.server.get_member(msg.author.id)
    server_member = cast(discord.Member, server_member)

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


async def remove_role(
    client: DuckClient, msg: discord.Message, role_id: int, role_name: str
) -> None:
    role = client.server.get_role(role_id)
    role = cast(discord.Role, role)

    server_member = client.server.get_member(msg.author.id)
    server_member = cast(discord.Member, server_member)

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
    examples = "!add cs1200, !add Computer Science"
    notes = "To see available roles, majors, and classes, use !list"

    names_no_courses = ["add", "join", "addrole", "joinrole"]
    description_no_courses = "Adds you to a role"
    usage_no_courses = "!add [role]"
    examples = "!add Computer Science"
    notes_no_courses = "To see available roles, use !list"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
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
                            client, msg, client.config["non_all_seer_id"], ""
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

    async def execute_reaction(
        self,
        client: DuckClient,
        reaction: discord.RawReactionActionEvent,
        channel: discord.TextChannel,
        msg: discord.Message,
        user: discord.User,
    ) -> bool:
        if (  # pylint: disable=too-many-boolean-expressions
            not client.config["ENABLE_COURSES"]
            or user.bot
            or channel.type is not discord.ChannelType.private
            or msg.author != client.user
            or user not in msg.mentions
            or " add " not in msg.content
            or reaction.emoji.name not in utils.EMOJI_NUMBERS
        ):
            return False

        if reaction.emoji.name == utils.NO_MATCHING_RESULTS_EMOTE:
            await utils.delay_send(msg.channel, client.messages["add_no_roles_match"])
            return False

        course_name, course_channel = await get_course_channel(
            client, msg.content, reaction.emoji.name
        )

        if not course_channel:
            await utils.delay_send(
                msg.channel,
                "Error: Unable to add course.  Please message an admin about this.",
            )
            return False

        try:
            overwrite = discord.PermissionOverwrite()
            overwrite.update(read_messages=True)
            await course_channel.set_permissions(user, overwrite=overwrite)  # type: ignore

            await utils.delay_send(
                msg.channel,
                client.messages["class_add_confirmation"].format(course_name),
            )

            # check if this user and channel is in the cache
            for past_user, past_channel in RECENTLY_ADDED_CACHE:
                if past_user == user.id and past_channel == channel.id:
                    return False

            RECENTLY_ADDED_CACHE.append((user.id, channel.id))
            if len(RECENTLY_ADDED_CACHE) > client.config["recent_class_cache_size"]:
                RECENTLY_ADDED_CACHE.pop(0)

            await utils.delay_send(
                channel,
                client.messages["class_add_welcome"].format(course_name, user.mention),
            )

        # pylint: disable=broad-except
        except Exception as e:
            await utils.delay_send(
                msg.channel, client.messages["err_adding_class"].format(e)
            )
            await utils.send_traceback(client, msg.content)

        return False


class RemoveClass(Command, ReactionTrigger):
    names = ["remove", "leave", "sub", "unregister", "drop"]
    description = "Removes you from roles and class specific channels"
    usage = "!remove [class code]"
    examples = "!remove Bio 1010, !remove Chemistry"

    names_no_courses = ["remove", "leave", "leaverole", "drop", "droprole"]
    description_no_courses = "Removes you from a role"
    usage_no_courses = "!remove [role]"
    examples_no_courses = "!remove Chemistry"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
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
                            client, msg, client.config["non_all_seer_id"], ""
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

    async def execute_reaction(
        self,
        client: DuckClient,
        reaction: discord.RawReactionActionEvent,
        channel: discord.TextChannel,
        msg: discord.Message,
        user: discord.User,
    ) -> bool:
        if (  # pylint: disable=too-many-boolean-expressions
            not client.config["ENABLE_COURSES"]
            or user.bot
            or channel.type is not discord.ChannelType.private
            or msg.author != msg.mentions
            or user not in msg.mentions
            or " remove " not in msg.content
        ):
            return False

        if reaction.emoji.name == utils.NO_MATCHING_RESULTS_EMOTE:
            await utils.delay_send(
                msg.channel, client.messages["remove_no_roles_match"]
            )

        if reaction.emoji.name not in utils.EMOJI_NUMBERS:
            return False

        line_start_idx = msg.content.index(reaction.emoji.name)
        start_idx = msg.content.index(":", line_start_idx) + 1
        end_idx = msg.content.index("\n", line_start_idx)

        course_name = msg.content[start_idx:end_idx].strip()
        async with client.lock:
            client.cursor.execute(
                f"SELECT channel_id FROM classes WHERE name = '{course_name}'"
            )
            channel_id = int(client.cursor.fetchone()[0])

        try:
            if channel_id != 0:
                course_channel = client.get_channel(channel_id)

                await course_channel.set_permissions(user, overwrite=None)  # type: ignore

            await utils.delay_send(
                msg.channel,
                client.messages["class_remove_confirmation"].format(course_name),
            )
        # pylint: disable=broad-except
        except Exception as e:
            await utils.delay_send(
                msg.channel, client.messages["err_removing_class"].format(e)
            )
            await utils.send_traceback(client, msg.content)

        return False
