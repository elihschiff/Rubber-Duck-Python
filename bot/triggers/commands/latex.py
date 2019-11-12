from . import Command
from .. import utils
import discord
import os
import requests
import json
import urllib.request
from PIL import Image, ImageOps
from latex import build_pdf
from pdf2image import convert_from_path
import math


class Latex(Command):
    names = ["tex", "latex"]
    description = "Renders an image of a latex command"
    description2 = """**Description:** Renders an image of a latex command
                      **Usage:** !latex [command]
                      **Example:** !latex \\cap, !latex \\frac{1}{2}
                      **Alternate names:** !tex"""
    needsContent = True

    async def execute_command(self, client, msg, content):
        try:
            url = "https://latex2image.joeraut.com/convert"
            filtered_content = urllib.parse.quote(content)
            payload = (
                "latexInput="
                + filtered_content
                + "&outputFormat=JPG&outputScale=1000%25"
            )
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            response = requests.request("POST", url, data=payload, headers=headers)
            dict = json.loads(response.text)
            url = r"https://latex2image.joeraut.com/" + dict["imageURL"]
            tmpLocationJPG = f"/tmp/" + dict["imageURL"][7:]
            urllib.request.urlretrieve(url, tmpLocationJPG)
            try:
                img = Image.open(tmpLocationJPG)
                borderSizeX = 5
                borderSizeY = 5
                img_with_border = ImageOps.expand(
                    img,
                    border=(borderSizeX, borderSizeY, borderSizeX, borderSizeY),
                    fill="#FFFFFF",
                )
                img_with_border.save(tmpLocationJPG)
                await msg.channel.send(file=discord.File(tmpLocationJPG))
            finally:
                os.remove(tmpLocationJPG)
        except:
            await msg.channel.send("Error rending LaTeX")
