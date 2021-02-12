from . import Command
from .. import utils
import io
import discord


class Recipe(Command):
    names = ["recipe", "food", "eat", "recipes", "cooking", "cook", "bake"]
    description = "Responds with a random recipe"
    usage = "!recipe"

    async def execute_command(self, client, msg, content, **kwargs):
        buffer = io.BytesIO()
        buffer.write(
            b"X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
        )
        buffer.seek(0)
        await utils.delay_send(msg.channel, file=discord.File(buffer, "recipe.txt"))
