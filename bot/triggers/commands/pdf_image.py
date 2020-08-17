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
        pdf_data = asyncio.run_coroutine_threadsafe(attach.read(), loop).result()
        images = convert_from_bytes(
            pdf_data,
            first_page=first_page,
            last_page=last_page,
            fmt="jpeg",
            use_pdftocairo=True,
        )
        return images
    except:
        return None


class PDF2Image(Command):
    names = ["pdfimage", "pdf2image"]
    description = "Converts an attached PDF into images for easy viewing"
    usage = "!pdfimage [start: optional] [end: optional]"
    examples = [
        "!pdfimage -- outputs all pages (max: 10)",
        "!pdfimage 2 -- outputs page 2",
        "!pdfimage 10 20 -- outputs pages 10-20",
    ]
    causes_spam = True

    async def execute_command(self, client, msg, content):
        if len(msg.attachments) == 0:
            return await utils.delay_send(
                msg.channel, "Error: no PDFs attached to message!"
            )

        # We enforce a range of 10 images max to prevent spam, limit server resource usage
        args = content.strip()

        if len(args) != 0:
            args = args.split(" ")

        lower_bound = 1
        upper_bound = 11

        try:
            if len(args) == 2:
                lower_bound = int(args[0])
                upper_bound = int(args[1])
            elif len(args) == 1:
                lower_bound = upper_bound = int(args[0])

            if (
                lower_bound < 0
                or upper_bound < lower_bound
                or (upper_bound - lower_bound > 10)
            ):
                raise ValueError()
        except:
            return await utils.delay_send(msg.channel, "Error: Invalid range")

        for attach in msg.attachments:
            if attach.size > 1e7:
                await utils.delay_send(
                    msg.channel, "Error: File too large (max size: 10MB)"
                )
                continue
            has_processed = False
            current_page = lower_bound
            # Save each page as a png file and send it out
            while current_page <= upper_bound:
                image = await loop.run_in_executor(
                    pool, convert_images, attach, current_page, current_page
                )
                if image is None or len(image) == 0:
                    break
                image = image[0]
                data = BytesIO()
                image.save(data, "jpeg")
                data.seek(0)
                await utils.delay_send(
                    msg.channel,
                    file=discord.File(data, filename=f"f{current_page}.jpeg"),
                )
                has_processed = True
                current_page += 1

            if not has_processed:
                return await utils.delay_send(
                    msg.channel,
                    "Error: failed to process attachment. Please check that the file is a PDF!",
                )
