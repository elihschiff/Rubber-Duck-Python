from . import Command
from .. import utils

import discord
import io


class Weather(Command):
    names = ["weather"]
    description = "Gets the weather."
    usage = "!weather [(optional) location]"
    examples = f"!weather 12180"

    async def execute_command(self, client, msg, content):
        # zipcode for Troy, NY is used if no arguments are passed
        content = "12180" if len(content) == 0 else content

        async with utils.get_aiohttp().get(
            f"http://wttr.in/{content}.png?0pq"
        ) as weather_request:
            if weather_request.status != 200:
                return await utils.delay_send(
                    msg.channel,
                    f"Failed to retrieve weather :-(. HTTP {weather_request.status}: ```{await weather_request.text()}```",
                )
            forecast = await weather_request.read()
            buffer = io.BytesIO()
            buffer.write(forecast)
            buffer.seek(0)
            await utils.delay_send(
                msg.channel, file=discord.File(buffer, filename="weather.png")
            )
