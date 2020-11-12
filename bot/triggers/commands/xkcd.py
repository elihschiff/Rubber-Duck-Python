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
    examples = f"!xkcd, !xkcd duck, !xkcd 537"

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
            async with utils.get_aiohttp().post(
                "https://relevant-xkcd-backend.herokuapp.com/search",
                data={"search": content},
            ) as request:
                text = await request.text()
            response = json.loads(text)

            if not response["success"] or len(response["results"]) == 0:
                await utils.delay_send(
                    msg.channel, client.messages["no_xkcd_found"].format(content)
                )
                return

            image_url = response["results"][0]["image"]
            title = response["results"][0]["title"]
            alt_text = response["results"][0]["titletext"]

        msg_to_send = "**" + title + ":** " + alt_text
        tmp_file = BytesIO()
        async with utils.get_aiohttp().get(image_url) as r:
            tmp_file.write(await r.read())
        tmp_file.seek(0)
        await msg.channel.send(msg_to_send, file=discord.File(tmp_file, "xkcd.png"))
