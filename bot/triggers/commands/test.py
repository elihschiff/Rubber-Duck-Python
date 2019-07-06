from . import Command
from .. import utils


class Test(Command):
    names = ["test"]
    description = "Test"
    needsContent = True

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, "pls8")
