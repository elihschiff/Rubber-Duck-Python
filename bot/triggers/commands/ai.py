from . import Command
from .. import utils


class AI(Command):
    names = ["ai", "academicintegrity", "academic_integrity"]
    description = "Reminds the channel about RPI's academic integrity policy"
    description2 = """**Description:** Reminds the channel about RPI's academic integrity policy
    				  **Usage:** !ai
    				  **Alternate names:** !academic integrity"""
    needsContent = False

    async def execute_command(self, client, msg, content):
        await utils.delay_send(msg.channel, client.messages["academic_integrity"], 0)
