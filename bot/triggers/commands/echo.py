from . import Command
from .. import utils


class Echo(Command):
    names = ["echo", "repeat"]
    description = "Echoes the given message"
    usage = "!echo [message]"

    async def execute_command(self, client, msg, content, **kwargs):
        if content:
            content.replace("@everyone", "@\u200beveryone")
            content.replace("@here", "@\u200bhere")
        else:
            content = "_ _"  # renders as invisible
        await utils.delay_send(msg.channel, content)
