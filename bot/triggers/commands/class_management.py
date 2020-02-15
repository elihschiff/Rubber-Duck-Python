from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger

import discord
import string
import json
import ast
import re

async def add_role(client, msg, role_id, role_name):
    role = client.SERVER.get_role(role_id)
    server_member = client.SERVER.get_member(msg.author.id)
    await server_member.add_roles(role)

    if role_name != "-------":
        await utils.delay_send(
            msg.channel, client.messages["add_role_confirmation"].format(role_name)
        )
    elif role_name == "-------":
        await msg.author.send(client.messages["add_hidden_role"])
        if msg.channel.type is not discord.ChannelType.private:
            utils.delay_send(msg.channel, f"Sorry, but I couldn't find the role `-------`.  Try using !list to view the server's roles.")


async def remove_role(client, msg, role_id, role_name):
    role = client.SERVER.get_role(role_id)
    server_member = client.SERVER.get_member(msg.author.id)
    await server_member.remove_roles(role)

    if role_name != "-------":
        await utils.delay_send(
            msg.channel, client.messages["remove_role_confirmation"].format(role_name)
        )
    elif role_name == "-------":
        await msg.author.send(client.messages["remove_hidden_role"])
        if msg.channel.type is not discord.ChannelType.private:
            utils.delay_send(msg.channel, f"Sorry, but I couldn't find the role `-------`.  Try using !list to view the server's roles.")

class AddClass(Command):
    names = ["add", "join", "register", "addrole", "joinrole"]
    description = "Adds you to a role"
    description2 = """**Description:** Adds you to a role
                      **Usage:** !add [role name]
                      **Example:** !add Class of 23, !add Mod
                      (To see available roles, use !list)"""
    needsContent = False

    def __init__(self):
        self.alphanum_re = re.compile("[^\w ]+")

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, client.messages["add_no_content"])
            return

        if content.lower() in ("mod", "admin", "server admin"):
            await utils.delay_send(msg.channel, client.messages["add_mod_message"])
            return

        for role in client.config["year_roles"].keys():
            if content.lower() == role.lower():
                await add_role(client, msg, client.config["year_roles"][role], role)
                return

        for major in client.config["major_roles"].keys():
            if content.lower() == major.lower():
                await add_role(client, msg, client.config["major_roles"][major], major)
                return

        for major in client.config["major_abbreviations"].keys():
            if content.lower() in client.config["major_abbreviations"][major]:
                await add_role(client, msg, client.config["major_roles"][major], major)
                return

        og_content = content
        if content.lower().endswith(" hall"):
            content = content[:-5]

        for dorm in client.config["dorm_roles"].keys():
            if content.lower() == dorm.lower():
                await add_role(
                    client, msg, client.config["dorm_roles"][dorm], dorm
                )
                return

        for dorm in client.config["dorm_abbreviations"].keys():
            if content.lower() in client.config["dorm_abbreviations"][dorm]:
                await add_role(
                    client, msg, client.config["dorm_roles"][dorm], dorm
                )
                return

        await utils.delay_send(msg.channel, f"Sorry, but I couldn't find the role `{utils.sanitized(og_content)}`.  Try using !list to view the server's roles.")

class RemoveClass(Command):
    names = ["remove", "leave", "sub", "unregister", "drop", "leaverole", "droprole", "removerole"]
    description = "Removes you from a role"
    description2 = """**Description:** Removes you from a role
                      **Usage:** !remove [role name]
                      **Example:** !remove Computer & Systems Engineering
                      (To see available roles, use !list)"""
    needsContent = False

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, client.messages["remove_no_content"])
            return

        for role in client.config["year_roles"].keys():
            if content.lower() == role.lower():
                await remove_role(
                    client, msg, client.config["year_roles"][role], role
                )
                return

        for major in client.config["major_roles"].keys():
            if content.lower() == major.lower():
                await remove_role(
                    client, msg, client.config["major_roles"][major], major
                )
                return

        for major in client.config["major_abbreviations"].keys():
            if content.lower() in client.config["major_abbreviations"][major]:
                await remove_role(
                    client, msg, client.config["major_roles"][major], major
                )
                return

        og_content = content
        if content.lower().endswith(" hall"):
            content = content[:-5]

        for dorm in client.config["dorm_roles"].keys():
            if content.lower() == dorm.lower():
                await remove_role(
                    client, msg, client.config["dorm_roles"][dorm], dorm
                )
                return

        for dorm in client.config["dorm_abbreviations"].keys():
            if content.lower() in client.config["dorm_abbreviations"][dorm]:
                await remove_role(
                    client, msg, client.config["dorm_roles"][dorm], dorm
                )
                return

        await utils.delay_send(msg.channel, f"Sorry, but I couldn't find the role `{utils.sanitized(og_content)}`.  Try using !list to view the server's roles.")
