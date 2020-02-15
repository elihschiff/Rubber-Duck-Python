from . import Command
from .. import utils

import discord
import string
import json
import ast


class ListClasses(Command):
    names = ["list", "roles"]
    description = "Lists all the roles which are able to be added."
    description2 = """**Description:** Lists all the roles in the server
                      **Usage:** !list
                      **Examples:** !list
                      **Alternate names:** !roles"""
    needsContent = False

    async def execute_command(self, client, msg, content):
        embed = discord.Embed(color=0xDCC308)
        roles_list = ""
        for role_name in client.config["year_roles"].keys():
            roles_list += role_name + "\n"
        embed.add_field(name="General Roles: `!add ROLE`", value=roles_list)

        roles_list = ""
        for role_name in client.config["major_roles"].keys():
            roles_list += role_name + "\n"
        embed.add_field(name="Major Roles: `!add MAJOR`", value=roles_list)

        dorms_list = ""
        for dorm_name in client.config["dorm_roles"].keys():
            dorms_list += dorm_name + "\n"
        embed.add_field(name="Dorm Roles: `!add DORM`", value=dorms_list)

        if msg.channel.type is not discord.ChannelType.private:
            await msg.channel.send("DMed!")

        await utils.delay_send(
            msg.author, client.messages["general_class_list_prelude"], embed=embed
        )
