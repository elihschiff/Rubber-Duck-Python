from . import Command
from .. import utils
import requests
import urllib.request
import re
import discord
from PIL import Image, ImageOps
import os
import math
import json


class Latex(Command):
    names = ["tex", "latex"]
    description = "Renders an image of a latex command"
    needsContent = True

    async def execute_command(self, client, msg, content):
        await utils.delay_send(
            msg.channel, "LATEX IS CURRENTLY NOT WORKING SORRY ABOUT THAT"
        )
        return

        data = json.dumps(
            {
                "auth": {"user": "guest", "password": "guest"},
                "latex": content,
                "resolution": 600,
                "color": "FFFFFF",
            }
        )

        response = requests.post(
            "http://latex2png.com/api/convert", data=data, verify=False
        )
        json_response = json.loads(response.text)

        if "url" in json_response:
            sub_url = json_response["url"]
            url = f"http://latex2png.com{sub_url}"
            image_id = sub_url.split("/")[2]
            tmpLocation = f"/tmp/{image_id}"
            urllib.request.urlretrieve(url, tmpLocation)

            img = Image.open(tmpLocation)
            borderSizeX, borderSizeY = img.size
            borderSizeX = math.ceil(borderSizeX / 20)
            borderSizeY = 0
            img_with_border = ImageOps.expand(
                img,
                border=(borderSizeX, borderSizeY, borderSizeX, borderSizeY),
                fill="#00000000",
            )
            img_with_border.save(tmpLocation)

            await msg.channel.send(file=discord.File(tmpLocation))
            os.remove(tmpLocation)
        else:
            await utils.delay_send(msg.channel, "ERROR IN LATEX")
