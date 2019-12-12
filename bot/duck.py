from discord.ext.commands import Bot

import aiohttp
import json


class DuckClient(Bot):
    def __init__(
        self,
        command_prefix="!",
        config_filename="config/config.json",
        messages_filename="config/messages.json",
        quacks_filename="config/quacks.txt",
        games_filename="config/games.txt",
    ):
        super().__init__(command_prefix=command_prefix)

        with open(config_filename, "r") as config_file:
            self.config = json.load(config_file)
        with open(messages_filename, "r") as messages_file:
            self.messages = json.load(messages_file)
        with open(quacks_filename, "r") as quacks_file:
            self.quacks = quacks_file.read().split("\n%\n")
        with open(games_filename, "r") as games_file:
            self.game_footers = games_file.read().split("\n%\n")

        self.aiohttp = aiohttp.ClientSession()

    async def on_ready(self):
        print(f"Connected as {self.user}!")
