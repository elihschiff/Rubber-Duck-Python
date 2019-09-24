from . import Command, all_commands
from .. import utils
import discord


class Help(Command):
    names = ["help"]
    description = "Echoes the given message"
    needsContent = False

    async def execute_command(self, client, msg, content):
        commands_arr = []
        for command in all_commands:
            if command.description:
                commands_arr.append(
                    f"**{command.prefixes[0]}{command.names[0]}:** {command.description}\n"
                )

        max_char_count = 2000
        commands_str = ""
        title = "General Commands"
        for line in commands_arr:
            if len(commands_str) + len(line) < max_char_count:
                commands_str += line
            else:
                response = discord.Embed(title=title, description=commands_str)
                await send_embed(msg, response, title)
                commands_str = line
                title = ""

        response = discord.Embed(title=title, description=commands_str)
        await send_embed(msg, response, title)


async def send_embed(msg, embed, title):
    if title:
        await utils.delay_send(msg.channel, "", embed=embed)
    else:
        await msg.channel.send("", embed=embed)
