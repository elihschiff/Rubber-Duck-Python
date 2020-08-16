from . import Command
from .. import utils
from pdf2image import convert_from_bytes
import discord
from io import BytesIO


class PDF2Image(Command):
    names = ["pdfimage", "pdf2image", "pdfpng", "pdf2png"]
    description = "Converts an attached PDF into images for easy viewing"
    usage = "!pdfimage [pdf attached to message]"
    causes_spam = True

    async def execute_command(self, client, msg, content):
        if len(msg.attachments) == 0:
            return await utils.delay_send(
                msg.channel, "Error: no PDFs attached to message!"
            )

        for attach in msg.attachments:
            pdf = await attach.to_file()
            try:
                images = convert_from_bytes(pdf.fp.read())
            except:
                return await utils.delay_send(
                    msg.channel,
                    f"Error: failed to process attachment {attach}. Please check that the file is a PDF!",
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
