import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class AI(Command):
    names = ["ai", "academicintegrity", "academic_integrity"]
    description = "Reminds the channel about RPI's academic integrity policy"
    usage = "!ai"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        await utils.delay_send(msg.channel, client.messages["academic_integrity"], 0)
