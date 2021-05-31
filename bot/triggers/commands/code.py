from . import Command
from .. import utils


class Code(Command):
    names = ["code"]
    description = "Sends information about my code"
    usage = "!code"
    show_in_help = True

    async def execute_command(self, client, msg, content, **kwargs):
        await utils.delay_send(msg.channel, client.messages["code"], 0.5, reply_to=msg)
