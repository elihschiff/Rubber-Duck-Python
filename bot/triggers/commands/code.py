import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Code(Command):
    names = ["code"]
    description = "Sends information about my code"
    usage = "!code"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        await utils.delay_send(msg.channel, client.messages["code"], 0.5)
