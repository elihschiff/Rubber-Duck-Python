from . import Command
from .. import utils
import requests


class Man(Command):
    names = ["man"]
    description = "Sends a link to a man page, if it exists"
    usage = "!man [command]"
    examples = f"!man grep"

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        args = content.split(" ")
        prgm = args[0]
        which_page = 0
        try:
            which_page = int(args[0])

            if len(args) < 2:
                await utils.delay_send(
                    msg.channel, f"Could not find man page for `{content}`"
                )
                return

            prgm = args[1]
        except:
            pass

        if which_page > 0:
            url = f"https://linux.die.net/man/{which_page}/{prgm}"
            r = requests.get(url)
            if "<h1>Not Found</h1>" in r.text or "<h1>Section " in r.text:
                await utils.delay_send(
                    msg.channel,
                    f"Could not find man page for `{prgm}` in section `{args[0]}`",
                )
            else:
                await utils.delay_send(msg.channel, url)
            return

        for page in range(0, 9):
            url = f"https://linux.die.net/man/{page}/{prgm}"
            r = requests.get(url)
            if "<h1>Not Found</h1>" not in r.text and "<h1>Section " not in r.text:
                await utils.delay_send(msg.channel, url)
                return

        await utils.delay_send(msg.channel, f"Could not find man page for `{content}`")
