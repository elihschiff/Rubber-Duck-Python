from . import Command
from .. import utils
import discord
import os
import json
import xkcd
from io import BytesIO


class Xkcd(Command):
    names = ["xkcd"]
    description = "Finds a relevant xkcd using a keyword or comic number"
    usage = "!xkcd [(optional) search term]"
    examples = "!xkcd, !xkcd duck, !xkcd 537"

    async def execute_command(self, client, msg, content, **kwargs):
        image_url = ""
        title = ""
        alt_text = ""
        if len(content) == 0:
            comic = xkcd.getRandomComic()
            image_url = comic.getImageLink()
            title = comic.getTitle()
            alt_text = comic.getAltText()
        elif content.isnumeric():
            try:
                comic = xkcd.getComic(int(content), silent=False)
                image_url = comic.getImageLink()
                title = comic.getTitle()
                alt_text = comic.getAltText()
            except:
                await utils.delay_send(
                    msg.channel, client.messages["no_xkcd_found"].format(content)
                )
                return
        else:
            tmp_file = BytesIO()
            async with utils.get_aiohttp().post(
                f"https://relevant-xkcd.com/@{content}",
            ) as req:
                tmp_file.write(await req.read())
            tmp_file.seek(0)
        await msg.channel.send(
            "",
            file=discord.File(tmp_file, "xkcd.png"),
            reference=msg,
            mention_author=True,
        )
