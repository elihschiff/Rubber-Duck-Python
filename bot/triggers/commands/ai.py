from . import Command
from .. import utils


class AI(Command):
    names = ["ai", "academicintegrity", "academic_integrity"]
    description = "Reminds the channel about RPI's academic integrity policy"
    usage = "!ai"

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, client.messages["academic_integrity"], 0)
