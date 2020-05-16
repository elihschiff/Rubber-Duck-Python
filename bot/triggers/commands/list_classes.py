import json
import string
from typing import Iterable, List

import discord

from . import Command
from .. import utils
from ...duck import DuckClient


def get_classes(client: DuckClient, subj: str) -> List[str]:
    client.cursor.execute(
        "SELECT * FROM classes WHERE departments LIKE ?", ("%" + subj.upper() + "%",),
    )
    records = client.cursor.fetchall()

    return [
        ", ".join(
            [
                "**" + course_code + "**"
                for course_code in json.loads(record[3].replace("'", '"'))
                if subj.upper() in course_code
            ]
        )
        + ": "
        + record[1]
        for record in records
    ]


def generate_embeds(prelude: str, classes: Iterable[str]) -> List[discord.Embed]:
    embeds = []
    class_str = ""

    for class_name in sorted(classes):
        class_str += class_name + "\n"
        if len(class_str) + len(prelude) >= 2000:
            embeds.append(discord.Embed(description=class_str, color=0xDCC308))
            class_str = ""

    if class_str:
        embeds.append(discord.Embed(description=class_str, color=0xDCC308))

    return embeds


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

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
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

        await self.send_list(client, msg, content)

    async def send_list(
        self, client: DuckClient, msg: discord.Message, subj: str
    ) -> None:
        classes = get_classes(client, subj)

        if not classes:
            await utils.delay_send(
                msg.channel, client.messages["dept_not_found"].format(subj.upper()),
            )
            return

        if msg.channel.type is not discord.ChannelType.private:
            await utils.delay_send(msg.channel, "DMed!")

        prelude = client.messages["class_list_prelude"].format(subj.upper())

        embeds = generate_embeds(prelude, classes)

        utils.delay_send(msg.author, prelude, embed=embeds[0])

        for embed in embeds[1:]:
            msg.author.send(prelude, embed=embed)

    async def general_listing(self, client: DuckClient, msg: discord.Message) -> None:
        embed = discord.Embed(color=0xDCC308)
        for role_category in client.roles["role_categories"]:
            roles_list = ""
            for role in role_category["roles"]:
                roles_list += role["name"] + "\n"
            category_name = role_category["category_name"]
            help_name = role_category["help_name"]
            embed.add_field(
                name=f"{category_name}: `!add {help_name}", value=roles_list
            )

        for school in client.roles["schools"]:
            dept_list = ""
            for dept in school["departments"]:
                dept_list += dept + "\n"
            help_name = school["help_name"]
            embed.add_field(
                name=f"{category_name}: `!list {help_name}", value=dept_list
            )

        if msg.channel.type is not discord.ChannelType.private:
            await utils.delay_send(msg.channel, "DMed!")

        await utils.delay_send(
            msg.author, client.messages["general_class_list_prelude"], embed=embed
        )

        await msg.author.send(client.messages["post_general_class_list"])
