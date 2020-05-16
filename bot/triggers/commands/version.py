import subprocess

import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Version(Command):
    names = ["version", "ver"]
    description = "Sends the Git commit which the bot is currently running on"
    usage = "!version"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        commit = (
            subprocess.check_output(["git", "log", "-n", "1"])
            .decode("utf-8")
            .strip(" \r\n")
        )
        await utils.delay_send(msg.channel, f"Current commit:\n```{commit}```")
