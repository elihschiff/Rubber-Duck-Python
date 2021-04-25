from . import Command
from .. import utils
from ..utils import sanitized
import random


class Choice(Command):
    names = ["choice", "choose"]
    description = "Chooses from a list of things"
    usage = "!choice [options]"
    examples = "!choice choose from these words"

    async def execute_command(self, client, msg, content, **kwargs):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}", reply_to=msg)
            return

        choices = content.split()
        choice = sanitized(random.choice(choices))
        await utils.delay_send(msg.channel, f"`{choice}`", reply_to=msg)
