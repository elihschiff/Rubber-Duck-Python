from . import Command
from .. import utils
import requests
import urllib.request
import re
import discord
from PIL import Image, ImageOps
import os
import math


class Latex(Command):
    names = ["tex", "latex"]
    description = "Renders an image of a latex command"
    needsContent = True

    async def execute_command(self, client, msg, content):
        data = requests.post(
            url="http://latex2png.com/",
            data={"latex": content, "res": 600, "color": "FFFFFF", "x": 62, "y": 28},
        )
        # print(data.text)
        name = re.search(r"latex_(.*)\.png", data.text).group()
        if name:
            url = f"http://latex2png.com/output//{name}"
            tmpLocation = f"/tmp/{name}"
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
