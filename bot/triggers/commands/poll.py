import discord

from bot.triggers.commands import Command
from ...duck import DuckClient


class Poll(Command):
    names = ["poll"]
    description = "Reacts with a thumbs up and thumbs down for polling on this message"
    usage = "!poll [(optional) message]"
    examples = "!poll, !poll ELi is better than Ben"

    should_type = False

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
