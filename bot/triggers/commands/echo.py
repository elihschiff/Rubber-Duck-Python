from . import Command
from .. import utils
import time


class Echo(Command):
    name = "echo"

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, content)
