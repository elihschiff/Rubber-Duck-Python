from .. import utils

from aiohttp import ClientResponseError
import cairosvg
import discord
import json
import os


def load(bot):
    usage = "!latex [command]"

    @bot.command(
        aliases=["tex"], help="Renders an image of a LaTeX command", usage=usage
    )
    async def latex(ctx, *args):
        command = " ".join(args)
        if not command:
            await ctx.send(f"Usage: `{usage}`")
            return

        async with ctx.typing():
            url = "https://latex2image.joeraut.com"
            payload = {
                "latexInput": command,
                "outputFormat": "SVG",
                "outputScale": "1000%",
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
            }

            try:
                response = await ctx.bot.aiohttp.post(
                    f"{url}/convert", data=payload, headers=headers
                )
                image_url = json.loads(await response.text())["imageURL"]
            except (ClientResponseError, KeyError):
                await ctx.send("Error rendering LaTeX")
                return

            tmp_location_png = f"/tmp/{image_url[7:-4]}.png"

            response = await ctx.bot.aiohttp.get(f"{url}/{image_url}")

            tmp_buf = await response.text()

            svg_buf = ""
            for line in tmp_buf.splitlines():
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
                svg_buf += line

            try:
                cairosvg.svg2png(
                    bytestring=str.encode(svg_buf), write_to=tmp_location_png
                )
                await ctx.channel.send(file=discord.File(tmp_location_png))
            finally:
                os.remove(tmp_location_png)
