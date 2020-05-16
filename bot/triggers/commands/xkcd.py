import json
import os
import urllib.request

import requests
import xkcd

import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Xkcd(Command):
    names = ["xkcd"]
    description = "Finds a relevant xkcd using a keyword or comic number"
    usage = "!xkcd [(optional) search term]"
    examples = "!xkcd, !xkcd duck, !xkcd 537"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
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
            # pylint: disable=bare-except
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
        tmp_location = "/tmp/xkcd_image.png"
        try:
            urllib.request.urlretrieve(image_url, tmp_location)

            await msg.channel.send(msg_to_send, file=discord.File(tmp_location))
        finally:
            os.remove(tmp_location)
