import os
import random

import discord
import png

from . import Command
from .. import utils


class RGB(Command):
    names = ["rgb", "color", "colour"]
    description = "Returns an image of the given color"

    # TODO: rewrite this to not need linter disabling
    # pylint: disable=too-many-branches
    async def execute_command(self, client, msg, content):
        args = content.split()
        if len(args) not in [0, 1, 3]:
            await utils.delay_send(
                msg.channel,
                msg="Usage: `!rgb [red] [green] [blue]` or `!rgb [hex color]`",
            )
            return
        if len(args) == 0:
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
        elif len(args) == 1:
            if args[0][0] == "#":
                args[0] = args[0][1:]
            if len(args[0]) != 6:
                try:
                    color = int(args[0])
                    if color < 0 or color > 255:
                        await utils.delay_send(
                            msg.channel, msg="Arguments must be in range [0,255]"
                        )
                        return
                    red = green = blue = color
                except ValueError:
                    await utils.delay_send(msg.channel, msg="Invalid hex or color")
                    return
            else:
                try:
                    red = int(args[0][0:2], 16)
                    green = int(args[0][2:4], 16)
                    blue = int(args[0][4:6], 16)
                except (ValueError, IndexError):
                    await utils.delay_send(msg.channel, msg="Invalid hex color")
                    return
        else:
            try:
                red = int(args[0])
                green = int(args[1])
                blue = int(args[2])
            except ValueError:
                await utils.delay_send(msg.channel, msg="All arguments must be ints")
                return
        if not (0 <= red <= 255 and 0 <= green <= 255 and 0 <= blue <= 255):
            await utils.delay_send(
                msg.channel, msg="Arguments must be in range [0,255]"
            )
            return
        row = (red, green, blue) * 128
        png_content = [row] * 128
        file_name = "/tmp/temp_" + str(msg.id) + ".png"
        try:
            with open(file_name, "wb") as png_f:
                writer = png.Writer(128, 128, greyscale=False)
                writer.write(png_f, png_content)
            await utils.delay_send(msg.channel, file=discord.File(file_name))
        finally:
            os.remove(file_name)
