from . import Command
from .. import utils
import requests
import os
import discord
from wand.image import Image
from wand.color import Color
import PIL

import ctypes
from wand.api import library

library.MagickAppendImages.argtypes = (ctypes.c_void_p, ctypes.c_bool)
library.MagickAppendImages.restype = ctypes.c_void_p


class pdfToPng(Command):
    names = ["pdf", "pdf-to-png", "png", "convert", "pdftopng"]
    description = "Converts a pdf file to a png"
    needsContent = False

    async def execute_command(self, client, msg, content):
        try:
            (attached_files_to_send, files_paths) = get_pdf_files(msg)

            for file in files_paths:
                with Image(filename=file, resolution=300) as pdf:
                    # Reset image stack
                    library.MagickResetIterator(pdf.wand)
                    # Append all pages into one new image
                    new_ptr = library.MagickAppendImages(pdf.wand, False)
                    library.MagickWriteImage(new_ptr, b"/tmp/discord/png_output.png")
                    library.DestroyMagickWand(new_ptr)

                    png = PIL.Image.open("/tmp/discord/png_output.png")
                    png.load()

                    background = PIL.Image.new("RGB", png.size, (255, 255, 255))
                    background.paste(png, mask=png.split()[3])  # 3 is the alpha channel
                    background.save("/tmp/discord/png_output.png", "PNG")
                    opened_file = [discord.File("/tmp/discord/png_output.png")]

                    await msg.channel.send("", files=opened_file)

            files_paths.append("/tmp/discord/png_output.png")
            remove_files(files_paths)
        except:
            await utils.delay_send(msg.channel, client.messages["pdf_png_failed"])


# returns the files to send and also the locations so they may be removed later
def get_pdf_files(msg):
    attached_file_locations = []
    for attachment in msg.attachments:
        if not attachment.filename.endswith(".pdf"):
            continue

        tmp_location = f"/tmp/{msg.id}-{attachment.filename}"
        r = requests.get(attachment.url, allow_redirects=True)
        open(tmp_location, "wb").write(r.content)

        attached_file_locations.append(tmp_location)

    attached_files_to_send = []
    for location in attached_file_locations:
        opened_file = discord.File(location)
        attached_files_to_send.append(opened_file)
    return attached_files_to_send, attached_file_locations


def remove_files(files_to_remove):
    for location in files_to_remove:
        os.remove(location)
