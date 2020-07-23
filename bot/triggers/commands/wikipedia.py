from bs4 import BeautifulSoup
import requests
import wikipediaapi

import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Wikipedia(Command):
    names = ["wiki", "wikipedia"]
    description = "Searches Wikipedia for a phrase"
    usage = "!wiki [phrase]"
    examples = "!wiki duck"

    def __init__(self) -> None:
        self.wiki = wikipediaapi.Wikipedia("en")

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if not content:
            page_link = "https://en.wikipedia.org/wiki/Special:Random"
            page_response = requests.get(page_link, timeout=30)
            page_content = BeautifulSoup(page_response.content, "html.parser")
            content = page_content.find(id="firstHeading").text

        page = self.wiki.page(content.replace(" ", "_"))
        if not page.exists():
            await utils.delay_send(
                msg.channel, f"Could not find wikipedia page for `{content}`"
            )
            return

        description = page.text[0:200]
        if len(page.text) > 200:
            description += "..."

        response = discord.Embed(
            title=content, url=page.fullurl, description=description
        )
        await utils.delay_send(msg.channel, "", embed=response)
