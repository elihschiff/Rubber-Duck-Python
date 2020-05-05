import json
import os
import urllib.request

import cairosvg
import discord
import requests

from . import Command
from .. import utils


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
            tmp_location_svg = f"/tmp/" + dict["imageURL"][7:]
            tmp_location_png = dict["imageURL"][7:-3] + "png"
            urllib.request.urlretrieve(url, tmp_location_svg)
            try:
                with open(tmp_location_svg, "r") as in_file:
                    buf = in_file.readlines()
                with open(tmp_location_svg, "w") as out_file:
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
                    file_obj=open(tmp_location_svg, "rb"), write_to=tmp_location_png
                )
                # don't use utils.delay_send() here since the above HTTP
                # likely took a while
                await msg.channel.send(file=discord.File(tmp_location_png))
            finally:
                os.remove(tmp_location_svg)
                os.remove(tmp_location_png)

        except:
            await utils.delay_send(msg.channel, "Error rending LaTeX")
