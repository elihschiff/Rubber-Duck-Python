from . import Command
from .. import utils


class Echo(Command):
    names = ["echo", "repeat"]
    description = "Echoes the given message"
    needsContent = True

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, content)
