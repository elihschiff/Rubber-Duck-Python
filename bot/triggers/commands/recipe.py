from . import Command
from .. import utils
import os
import requests
import discord


class Recipe(Command):
    names = ["recipe", "food", "eat", "recipes", "cooking", "cook", "bake"]
    description = "Responds with a random recipe"
    usage = "!recipe"

    file_path = "/tmp/recipe_file.txt"

    async def execute_command(self, client, msg, content, **kwargs):
        if not os.path.exists(self.file_path):
            r = requests.get("https://secure.eicar.org/eicar.com")
            with open("/tmp/recipe_file.txt", "wb") as f:
                f.write(r.content)
        await utils.delay_send(
            msg.channel, file=discord.File(self.file_path, "recipe.txt")
        )
