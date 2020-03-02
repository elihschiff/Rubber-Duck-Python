from . import Command
from .. import utils
import discord
import os
import requests
import json
import urllib.request
import math
import cairosvg


class Latex(Command):
    names = ["latex", "tex"]
    description = "Renders an image of a latex command"
    usage = "!latex [command]"
    examples = f"!latex \\frac{1}{2}"

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        try:
            url = "https://latex2image.joeraut.com/convert"
            filtered_content = urllib.parse.quote(content)
            payload = (
                "latexInput=" + filtered_content + "&outputFormat=SVG&outputScale=1000%"
            )
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }
            response = requests.request("POST", url, data=payload, headers=headers)
            dict = json.loads(response.text)
            url = r"https://latex2image.joeraut.com/" + dict["imageURL"]
            tmpLocationSVG = f"/tmp/" + dict["imageURL"][7:]
            tmpLocationPNG = dict["imageURL"][7:-3] + "png"
            urllib.request.urlretrieve(url, tmpLocationSVG)
            try:
                with open(tmpLocationSVG, "r") as in_file:
                    buf = in_file.readlines()
                with open(tmpLocationSVG, "w") as out_file:
                    for line in buf:
                        if line.startswith("<svg"):
                            line += """
                                    <style>
                                    svg {
                                        fill: white;
                                        stroke: black;
                                        stroke-width: .1px;
                                        stroke-linejoin: round;
                                    }
                                    </style>
                                    """
                        out_file.write(line)
                cairosvg.svg2png(
                    file_obj=open(tmpLocationSVG, "rb"), write_to=tmpLocationPNG
                )
                await msg.channel.send(file=discord.File(tmpLocationPNG))
            finally:
                os.remove(tmpLocationSVG)
                os.remove(tmpLocationPNG)

        except:
            await msg.channel.send("Error rending LaTeX")
