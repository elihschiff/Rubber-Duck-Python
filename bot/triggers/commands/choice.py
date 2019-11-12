from . import Command
from .. import utils
import random


class Choice(Command):
    names = ["choice", "choose"]
    description = "Chooses from a list of things"
    description2 = """**Description:** Chooses from a list of things
                      **Usage:** !choice [message]
                      **Example:** !choice choose from these words
                      **Alternate names:** !choose"""
    needsContent = True

    async def execute_command(self, client, msg, content):
        choices = content.split()
        choice = random.choice(choices).replace("`", "'")
        await utils.delay_send(msg.channel, f"`{choice}`")
