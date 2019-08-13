from . import Command
from .. import utils
import discord
import wikipediaapi


class Wikipedia(Command):
    names = ["wiki", "wikipedia"]
    description = "Searches Wikipedia for a phrase"
    needsContent = False

    def __init__(self):
        self.wiki = wikipediaapi.Wikipedia("en")

    async def execute_command(self, client, msg, content):
        page = self.wiki.page(content.replace(" ", "_"))
        if not page.exists():
            await msg.channel.send(
                f"Could not find wikipedia page for `{content}`"
            )
            return

        description = page.text[0:200]
        if len(page.text) > 200:
            description += "..."

        response = discord.Embed(
            title=content, url=page.fullurl, description=description
        )
        await utils.delaysend(msg.channel, "", embed=response)
