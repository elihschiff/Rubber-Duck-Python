import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Issue(Command):
    names = ["issue", "issues"]
    description = "Tells user how to report a change"
    usage = "!issue"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        await utils.delay_send(msg.channel, client.messages["issue"], 0)
