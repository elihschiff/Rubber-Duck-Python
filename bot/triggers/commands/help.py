from . import Command, all_commands
from .. import utils
import discord


class Help(Command):
    names = ["help"]
    description = "Echoes the given message"
    needsContent = False

    async def execute_command(self, client, msg, content):
        response = discord.Embed()
        commands_str = ""
        for command in all_commands:
            commands_str += (
                f"**{command.prefixes[0]}{command.names[0]}:** {command.description}\n"
            )
        response.add_field(name="General Commands", value=commands_str, inline=True)
        await msg.channel.send(embed=response)
