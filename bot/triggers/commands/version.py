from . import Command
from .. import utils
import subprocess


class Version(Command):
    names = ["version", "ver"]
    description = "Sends the current Git commit for the local repository"
    needsContent = False

    async def execute_command(self, client, msg, content):
        commit = (
            subprocess.check_output(["git", "rev-parse", "HEAD"])
            .decode("utf-8")
            .strip(" \r\n")
        )
        await utils.delay_send(
            msg.channel, f"Rubber Duck is currently running commit {commit}"
        )