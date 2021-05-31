from . import Command
from .. import utils

import discord
import io
from urllib.parse import quote_plus


class Weather(Command):
    names = ["weather"]
    description = "Gets the weather."
    usage = "!weather [(optional) location]"
    examples = "!weather 12180"
    show_in_help = True

    async def send_image(self, msg, request, msg_text=""):
        forecast = await request.read()
        buffer = io.BytesIO()
        buffer.write(forecast)
        buffer.seek(0)

        return await utils.delay_send(
            msg.channel,
            msg=msg_text,
            file=discord.File(buffer, filename="weather.png"),
            reply_to=msg,
        )

    async def execute_command(self, client, msg, content, **kwargs):
        # zipcode for Troy, NY is used if no arguments are passed
        content = "12180" if len(content) == 0 else content

        async with utils.get_aiohttp().get(
            f"https://wttr.in/{quote_plus(content)}.png?0pq&background=36393e"
        ) as weather_request:
            if weather_request.status != 200:
                try:
                    weather_request_text = await weather_request.text()
                    return await utils.delay_send(
                        msg.channel,
                        f"Failed to retrieve weather :-(. HTTP {weather_request.status}: ```{weather_request_text}```",
                        reply_to=msg,
                    )
                except UnicodeDecodeError:
                    # Who sends image data in a 404?
                    return await self.send_image(
                        msg,
                        weather_request,
                        f"Failed to retrieve weather :-(. HTTP {weather_request.status}",
                    )

            return await self.send_image(msg, weather_request)
