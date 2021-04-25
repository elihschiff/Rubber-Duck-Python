from . import Command
from .. import utils
from urllib.parse import urlencode


class Lmdtfy(Command):
    names = ["lmdtfy", "search"]
    description = "Helps someone look something up on the superior search engine"
    usage = "!lmdtfy [query]"
    examples = "!lmdtfy Does water boil in space?"

    async def execute_command(self, client, msg, content, **kwargs):
        if not content:
            content = "How do I think of what to search?"

        url = "https://lmgtfy.com/?s=d&" + urlencode({"q": content})
        await utils.delay_send(msg.channel, url, 1, reply_to=msg)


class Lmgtfy(Command):
    names = ["lmgtfy"]
    description = "Helps someone look something up on the inferior search engine"
    usage = "!lmgtfy [query]"
    examples = "!lmgtfy Why am I not using DuckDuckGo?"

    async def execute_command(self, client, msg, content, **kwargs):
        if not content:
            content = "How do I think of what to search?"

        url = "https://lmgtfy.com/?" + urlencode({"q": content})
        await utils.delay_send(msg.channel, url, 1, reply_to=msg)
