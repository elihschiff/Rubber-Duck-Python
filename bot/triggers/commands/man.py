import requests

import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Man(Command):
    names = ["man"]
    description = "Sends a link to a man page, if it exists"
    usage = "!man [(optional) page number] [command]"
    examples = "!man grep"

    valid_man_pages = ["1", "2", "3", "4", "5", "6", "7", "8", "l", "n"]

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        args = content.split(" ")
        if len(args) > 1:
            if args[0].lower() in self.valid_man_pages:
                page = args[0].lower()
            else:
                await utils.delay_send(
                    msg.channel,
                    f"`{utils.sanitized(args[0])}` is not a valid man page",
                )
                return

            program = args[1]
            await self.check_man_page(msg.channel, page, program, True)
        else:
            program = args[0]
            for page in self.valid_man_pages:
                if await self.check_man_page(msg.channel, page, program, True):
                    return

        await utils.delay_send(msg.channel, f"Could not find man page for `{content}`")

    async def check_man_page(
        self,
        channel: utils.Sendable,
        page: str,
        program: str,
        send_when_not_found: bool,
    ) -> bool:
        url = f"https://linux.die.net/man/{page}/{program}"
        man_page = requests.get(url)
        if "<h1>Not Found</h1>" in man_page.text or "<h1>Section " in man_page.text:
            if send_when_not_found:
                await utils.delay_send(
                    channel,
                    f"Could not find man page for `{program}` in section `{page}`",
                )
            return False
        else:
            await utils.delay_send(channel, url)
            return True
