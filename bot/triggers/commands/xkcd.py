from . import Command
from .. import utils
import discord
import requests
import urllib.request
import os
import json
import xkcd


class Xkcd(Command):
    names = ["xkcd"]
    description = "Finds a relevant xkcd using a keyword or comic number"
    usage = "!xkcd [(optional) search term]"
    examples = f"!xkcd, !xkcd duck, !xkcd 435"

    async def execute_command(self, client, msg, content):
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

            response = json.loads(
                requests.post(
                    "https://relevant-xkcd-backend.herokuapp.com/search",
                    data={"search": content},
                ).text
            )

            if not response["success"] or len(response["results"]) == 0:
                await utils.delay_send(
                    msg.channel, client.messages["no_xkcd_found"].format(content)
                )
                return

            image_url = response["results"][0]["image"]
            title = response["results"][0]["title"]
            alt_text = response["results"][0]["titletext"]

        msg_to_send = "**" + title + ":** " + alt_text
        tmpLocation = f"/tmp/xkcd_image.png"
        urllib.request.urlretrieve(image_url, tmpLocation)

        await msg.channel.send(msg_to_send, file=discord.File(tmpLocation))
        os.remove(tmpLocation)
