from . import Command
from .. import utils
import urllib
from bs4 import BeautifulSoup
import requests
import discord


class Steam(Command):
    names = ["steam"]
    description = "Gets some steam games"
    needsContent = True

    async def execute_command(self, client, msg, content):
        async with msg.channel.typing():
            filtered_content = urllib.parse.quote(content)
            page_link = (
                "https://store.steampowered.com/search/?term=" + filtered_content
            )
            page_response = requests.get(page_link, timeout=5)
            page_content = page_content = BeautifulSoup(
                page_response.content, "html.parser"
            )
            rows = page_content.find(id="search_resultsRows")
            if rows == None:
                await msg.channel.send(
                    f'Unable to find any games matching "' + content + '"'
                )
                return
            title = rows.find("span", {"class": "title"})
            link = rows.find("a")["href"]

            game_page_response = requests.get(link, timeout=5)
            game_page_content = BeautifulSoup(game_page_response.content, "html.parser")
            desc = game_page_content.find(
                "div", {"class": "game_description_snippet"}
            ).text
            price_block = game_page_content.find(
                "div", {"class": "game_purchase_price"}
            )
            if price_block == None:
                price_block = game_page_content.find(
                    "div", {"class": "discount_final_price"}
                )
            price = price_block.text

            desc += "\n\nPrice: " + price
            img = game_page_content.find("img", {"class": "game_header_image_full"})[
                "src"
            ]
            embed = discord.Embed(
                title=title.text, description=desc, color=0x00FF00, url=link
            )
            embed.set_thumbnail(url=img)
            await msg.channel.send(embed=embed)
