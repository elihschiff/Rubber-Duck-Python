from . import Command
from .. import utils
from urllib.parse import urlencode


class Lmdtfy(Command):
    names = ["lmdtfy", "search"]
    description = "Helps someone look something up on the superior search engine"
    description2 = """**Description:** Helps someone look something up on the superior search engine
                      **Usage:** !lmgtfy Does water boil in space?
                      **Alternate names:** !search"""
    needsContent = True

    async def execute_command(self, client, msg, content):
        url = "https://lmgtfy.com/?s=d&" + urlencode({"q": content})
        await utils.delay_send(msg.channel, url, 1)


class Lmgtfy(Command):
    names = ["lmgtfy"]
    description = "Helps someone look something up on the inferior search engine"
    description2 = """**Description:** Helps someone look something up on the inferior search engine
                      **Usage:** !lmgtfy Why does water boil in space?"""
    needsContent = True

    async def execute_command(self, client, msg, content):
        url = "https://lmgtfy.com/?" + urlencode({"q": content})
        await utils.delay_send(msg.channel, url, 1)
