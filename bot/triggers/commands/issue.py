from . import Command
from .. import utils


class Issue(Command):
    names = ["issue", "issues"]
    description = "Tells user how to report a change"
    description2 = """**Description:** Tells user how to report a change
                      **Usage:** !issue
                      **Alternate name:** !issues"""
    needsContent = False

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, client.messages["issue"], 0)
