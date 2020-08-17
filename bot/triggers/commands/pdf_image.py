from . import Command
from .. import utils
from concurrent.futures import ThreadPoolExecutor
from pdf2image import convert_from_bytes
from io import BytesIO

import asyncio
import discord

pool = ThreadPoolExecutor(max_workers=1)
loop = asyncio.get_event_loop()


def convert_images(attach, first_page, last_page):
    try:
        pdf = asyncio.run_coroutine_threadsafe(attach.to_file(), loop).result()
        images = convert_from_bytes(
            pdf.fp.read(), first_page=first_page, last_page=last_page
        )
        return images
    except:
        return None


class PDF2Image(Command):
    names = ["pdfimage", "pdf2image", "pdfpng", "pdf2png"]
    description = "Converts an attached PDF into images for easy viewing"
    usage = "!pdfimage [start: optional] [end: optional]"
    examples = [
        "!pdfimage -- outputs all pages (max: 50)",
        "!pdfimage 2 -- outputs page 2",
        "!pdfimage 10 40 -- outputs pages 10-40",
    ]
    causes_spam = True

    async def execute_command(self, client, msg, content):
        if len(msg.attachments) == 0:
            return await utils.delay_send(
                msg.channel, "Error: no PDFs attached to message!"
            )

        # We enforce a range of 50 images max to prevent spam, limit server resources
        args = content.strip().split(" ")
        lower_bound = 1
        upper_bound = 51

        try:
            if len(args) == 2:
                lower_bound = int(args[0])
                upper_bound = int(args[1])
            elif len(args) == 1:
                lower_bound = upper_bound = int(args[0])
        except ValueError:
            lower_bound = 1
            upper_bound = 51

        if (
            lower_bound < 0
            or upper_bound < lower_bound
            or (upper_bound - lower_bound > 50)
        ):
            return await utils.delay_send(msg.channel, "Error: Invalid range")

        for attach in msg.attachments:
            images = await loop.run_in_executor(
                pool, convert_images, attach, lower_bound, upper_bound
            )

            if images is None:
                return await utils.delay_send(
                    msg.channel,
                    "Error: failed to process attachment. Please check that the file is a PDF!",
                )

            # Save each page as a png file and send it out
            files = []
            i = 1
            while len(images) > 0:
                data = BytesIO()
                images[0].save(data, "png")
                del images[0]
                data.seek(0)
                files.append(discord.File(data, filename=f"f{i}.png"))
                i += 1
                # discord.py can only send 10 files per bulk operation
                if len(files) == 10 or len(images) == 0:
                    await utils.delay_send(msg.channel, files=files)
                    files = []
