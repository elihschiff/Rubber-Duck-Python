import requests

import discord

from . import Command
from .. import utils
from ...duck import DuckClient


class Weather(Command):
    names = ["weather"]
    description = "Gets the weather."
    usage = "!weather [(optional) location]"
    examples = "!weather 12180"

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        # zipcode for Troy, NY is used if no arguments are passed
        content = "12180" if len(content) == 0 else content

        weather_request = requests.get(f"https://wttr.in/{content}?0ATnF")
        await utils.delay_send(msg.channel, f"```bash\n{weather_request.text}```")
