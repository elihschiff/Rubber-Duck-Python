from . import Command
from .. import utils


class Code(Command):
    names = ["code"]
    description = "Sends information about my code"
    description2 = """**Description:** Sends information about my code
				  **Usage:** !code"""
    needsContent = False

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, client.messages["code"], 0.5)
