from . import Command, all_commands
from .. import utils
import discord


class Help(Command):
    names = ["help"]
    description = "Lists commands and their description"
    needsContent = False

    async def execute_command(self, client, msg, content):
        args = content.split(" ")
        # if a specific command for help was entered
        if args[0].strip() != "":
            for command in all_commands:
                for name in command.names:
                    name1 = name
                    name2 = f"{command.prefixes[0]}{name}"
                    if name1 == args[0] or name2 == args[0]:
                        title = f"{name} command:"
                        commands_str = command.description2
                        response = discord.Embed(title=title, description=commands_str)
                        await send_embed(msg, response, title)
                        return
            await utils.delay_send(
                msg.channel, f'Could not find command "{args[0]}".\n'
            )

        # otherwise, list all commands and their descriptions
        await utils.delay_send(
            msg.channel,
            'Here are all general commands. To get help for a specific command,\
 write "!help [command name]" (ex: !help add).\n',
        )

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
    # only delay send if it's the first message
    if title:
        await utils.delay_send(msg.channel, "", embed=embed)
    else:
        await msg.channel.send("", embed=embed)
