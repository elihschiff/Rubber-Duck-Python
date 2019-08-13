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
    print(matches)
    results = []
    for match in matches:
        class_name = real_name_list[class_list.index(match[0])]
        if class_name not in results:
            results.append(class_name)
        if len(results) >= max_results:
            break

    return results


class AddClass(Command, ReactionTrigger):
    names = ["add", "search"]
    description = "Adds you to hidden class specific channels"
    needsContent = True

    connection = sqlite3.connect("classes.db")
    c = connection.cursor()

    async def execute_command(self, client, msg, content):
        options = fuzzy_search(self.c, content, 5)

        print(options)

        await utils.generate_react_menu(
            msg,
            msg.author.id,
            f", Your search for **{content}** retrieved these results.\nClick the corresponding reaction to add that class:",
            5,
            options,
            "No results match",
        )

    async def execute_reaction(self, client, reaction, user):
        return
