from . import Command
from .. import utils
import os
import nextcord
import png
import random
from io import BytesIO


class RGB(Command):
    names = ["rgb", "color", "colour"]
    description = "Returns an image of the given color"

    async def execute_command(self, client, msg, content, **kwargs):
        args = content.split()
        if len(args) not in [0, 1, 3]:
            await utils.delay_send(
                msg.channel,
                msg="Usage: `!rgb [red] [green] [blue]` or `!rgb [hex color]`",
                reply_to=msg,
            )
            return
        if len(args) == 0:
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
        elif len(args) == 1:
            if args[0][0] == "#":
                args[0] = args[0][1:]
            if len(args[0]) != 6:
                try:
                    c = int(args[0])
                    if c < 0 or c > 255:
                        await utils.delay_send(
                            msg.channel,
                            msg="Arguments must be in range [0,255]",
                            reply_to=msg,
                        )
                        return
                    r = g = b = c
                except:
                    await utils.delay_send(
                        msg.channel, msg="Invalid hex or color", reply_to=msg
                    )
                    return
            else:
                try:
                    r = int(args[0][0:2], 16)
                    g = int(args[0][2:4], 16)
                    b = int(args[0][4:6], 16)
                except:
                    await utils.delay_send(
                        msg.channel, msg="Invalid hex color", reply_to=msg
                    )
                    return
        else:
            try:
                r = int(args[0])
                g = int(args[1])
                b = int(args[2])
            except:
                await utils.delay_send(
                    msg.channel, msg="All arguments must be ints", reply_to=msg
                )
                return
        if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
            await utils.delay_send(
                msg.channel, msg="Arguments must be in range [0,255]", reply_to=msg
            )
            return
        row = ()
        for i in range(0, 128):
            row = row + (r, g, b)
        p = []
        for i in range(0, 128):
            p.append(row)
        w = png.Writer(128, 128, greyscale=False)
        png_data = BytesIO()
        w.write(png_data, p)
        png_data.seek(0)
        await utils.delay_send(
            msg.channel, file=nextcord.File(png_data, "rgb.png"), reply_to=msg
        )
