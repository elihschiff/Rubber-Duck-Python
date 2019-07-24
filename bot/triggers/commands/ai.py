from . import Command
from .. import utils


class AI(Command):
    names = ["ai", "academic integrity"]
    description = "Reminds the channel about RPI's academic integrity policy"
    needsContent = False

    async def execute_command(self, client, msg, content):
        await utils.delay_send(
            msg.channel, client.messages["academic_integrity"], 0
        )
