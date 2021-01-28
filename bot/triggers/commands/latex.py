from . import Command
from .. import utils
import discord
import json
import cairosvg
from io import StringIO, BytesIO
import urllib


class Latex(Command):
    names = ["latex", "tex"]
    description = "Renders an image of a latex command"
    usage = "!latex [command]"
    examples = f"!latex \\frac{1}{2}"

    async def execute_command(self, client, msg, content, **kwargs):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        try:
            url = "https://e1kf0882p7.execute-api.us-east-1.amazonaws.com/default/latex2image"
            filtered_content = urllib.parse.quote(content)

            payload = {
                "latexInput": filtered_content,
                "outputFormat": "SVG",
                "outputScale": "1000%",
            }
            headers = {
                "Content-Type": "application/json; charset=UTF-8",
                "User-Agent": "slithering-duck/1.0 (+https://discord.com/rpi)",
            }
            async with utils.get_aiohttp().post(
                url, data=json.dumps(payload), headers=headers
            ) as response:
                response.raise_for_status()
                dict = json.loads(await response.text())

            url = dict["imageUrl"]

            async with utils.get_aiohttp().get(url, headers=headers) as response:
                tmpLocationSVG = (await response.text()).replace(
                    "</svg>",
                    "<style> svg { fill: white; stroke: black; stroke-width: .1px; stroke-linejoin: round; } </style> </svg>",
                )
            await utils.delay_send(
                msg.channel,
                file=discord.File(
                    BytesIO(cairosvg.svg2png(file_obj=StringIO(tmpLocationSVG))),
                    f"{content}.png",
                ),
            )
        except:
            await utils.delay_send(msg.channel, "Error rending LaTeX")
