from . import Command
from .. import utils
from urllib.parse import urlencode


class Lmdtfy(Command):
    names = ["lmdtfy", "search"]
    description = "Helps someone look something up on the superior search engine"
    usage = f"{prefixes[0]}lmdtfy [query]"
    examples = f"{prefixes[0]}lmdtfy Does water boil in space?"

    async def execute_command(self, client, msg, content):
        if not content:
            content = "How do I think of what to search?"

        url = "https://lmgtfy.com/?s=d&" + urlencode({"q": content})
        await utils.delay_send(msg.channel, url, 1)


class Lmgtfy(Command):
    names = ["lmgtfy"]
    description = "Helps someone look something up on the inferior search engine"
    usage = f"{prefixes[0]}lmgtfy [query]"
    examples = f"{prefixes[0]}lmgtfy Why am I not using DuckDuckGo?"

    async def execute_command(self, client, msg, content):
        if not content:
            content = "How do I think of what to search?"

        url = "https://lmgtfy.com/?" + urlencode({"q": content})
        await utils.delay_send(msg.channel, url, 1)
