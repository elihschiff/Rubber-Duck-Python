from . import Command
from .. import utils


class Issue(Command):
    names = ["issue", "issues"]
    description = "Tells user how to report a change"
    usage = "!issue"

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, client.messages["issue"], 0)
