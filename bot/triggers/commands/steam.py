from . import Command
from .. import utils
import urllib
from bs4 import BeautifulSoup
import discord


class Steam(Command):
    names = ["steam", "epic"]
    description = "Looks up a game on the Steam store"
    usage = "!steam [game name]"
    examples = "!steam team fortress 2"

    async def execute_command(self, client, msg, content, **kwargs):
        if not content:
            await utils.delay_send(msg.channel, "<https://store.steampowered.com>")
            return

        try:
            filtered_content = urllib.parse.quote(content)
            page_link = (
                "https://store.steampowered.com/search/?term=" + filtered_content
            )
            async with utils.get_aiohttp().get(page_link) as page_response:
                page_content = BeautifulSoup(await page_response.read(), "html.parser")
            rows = page_content.find(id="search_resultsRows")
            if rows == None:
                await msg.channel.send(
                    f"Unable to find any games matching `{utils.sanitized(content)}`"
                )
                return
            title = rows.find("span", {"class": "title"})
            link = rows.find("a")["href"]
            cookies = {
                "wants_mature_content": "1",
                "birthtime": "376030801",
                "lastagecheckage": "1-0-1982",
            }
            async with utils.get_aiohttp().get(
                link, cookies=cookies
            ) as game_page_response:
                game_page_content = BeautifulSoup(
                    await game_page_response.read(), "html.parser"
                )
            desc = game_page_content.find("div", {"class": "game_description_snippet"})
            img = None
            if desc == None:
                desc = "No snippet available for this game"
            else:
                desc = desc.text
            price_block = game_page_content.find(
                "div", {"class": "game_purchase_price"}
            )
            if price_block == None:
                price_block = game_page_content.find(
                    "div", {"class": "discount_final_price"}
                )
            if price_block != None:
                price = price_block.text
                desc += "\n\nPrice: " + price
            else:
                desc += "\n\nPrice: TBA"
            img = game_page_content.find("img", {"class": "game_header_image_full"})
            if img != None:
                img = img["src"]
            embed = discord.Embed(
                title=title.text, description=desc, color=0x00FF00, url=link
            )
            if img != None:
                embed.set_thumbnail(url=img)
            await utils.delay_send(msg.channel, "", 0, embed=embed)
        except Exception as ex:
            await msg.channel.send("An error occured when finding the game")
            await utils.sendTraceback(client, msg.content)
