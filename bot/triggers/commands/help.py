import discord

from . import Command, ALL_COMMANDS
from .. import utils


class Help(Command):
    names = ["help"]
    description = "Lists commands and their description"

    async def execute_command(self, client, msg, content):
        if content:
            await self.send_single_help(content, client, msg.channel)
        else:
            if msg.channel.type is not discord.ChannelType.private:
                await utils.delay_send(msg.channel, "DMed!")
            await self.send_all_help(client, msg.author)

    async def send_single_help(self, client, cmd_name, channel):
        for command in ALL_COMMANDS:
            for name in utils.get_correct_attr(command, "names", client):
                if name == cmd_name:
                    names = utils.get_correct_attr(command, "names", client)
                    desc = utils.get_correct_attr(command, "description", client)
                    usage = utils.get_correct_attr(command, "usage", client)
                    examples = utils.get_correct_attr(command, "examples", client)
                    notes = utils.get_correct_attr(command, "notes", client)

                    embed_title = f"{names[0]} command:"
                    command_help = ""
                    if desc:
                        command_help += f"\n**Description**: {desc}"
                    if usage:
                        command_help += f"\n**Usage**: {usage}"
                    if examples:
                        command_help += f"\n**Examples**: {examples}"
                    if len(names) > 1:
                        alt_name_str = ", ".join(
                            [f"{command.prefixes[0]}{name}" for name in names[1:]]
                        )
                        command_help += f"\n**Alternative names**: {alt_name_str}"
                    if notes:
                        command_help += f"\n**Notes**: {notes}"

                    response = discord.Embed(
                        title=embed_title, description=command_help
                    )
                    await send_embed(channel, response, embed_title)
                    return
        await utils.delay_send(channel, f'Could not find command "{cmd_name}".\n')

    async def send_all_help(self, client, channel):
        await utils.delay_send(
            channel,
            'Here are all general commands. To get help for a specific command, write "!help [command name]" (ex: !help add).\n',
        )

        commands_arr = []
        for command in ALL_COMMANDS:
            command_names = utils.get_correct_attr(command, "names", client)
            command_desc = utils.get_correct_attr(command, "description", client)
            if command.description:
                commands_arr.append(
                    f"**{command.prefixes[0]}{command_names[0]}:** {command_desc}\n"
                )

        max_char_count = 2000
        commands_str = ""
        title = "General Commands"
        for line in commands_arr:
            if len(commands_str) + len(line) < max_char_count:
                commands_str += line
            else:
                response = discord.Embed(title=title, description=commands_str)
                await send_embed(channel, response, title)
                commands_str = line
                title = ""

        response = discord.Embed(title=title, description=commands_str)
        await send_embed(channel, response, title)


async def send_embed(channel, embed, title):
    # only delay send if it's the first message
    if title:
        await utils.delay_send(channel, "", embed=embed)
    else:
        await channel.send("", embed=embed)
