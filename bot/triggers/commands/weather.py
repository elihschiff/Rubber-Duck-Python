from . import Command
from .. import utils
import requests


class Weather(Command):
    names = ["weather"]
    description = "Gets the weather."
    usage = "!weather [(optional) location]"
    examples = f"!weather 12180"

    async def execute_command(self, client, msg, content):
        # zipcode for Troy, NY is used if no arguments are passed
        content = "12180" if len(content) == 0 else content

        weather_request = requests.get(f"https://wttr.in/{content}?0ATnF")
        await utils.delay_send(msg.channel, f"```bash\n{weather_request.text}```")
