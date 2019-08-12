import sys
import discord
import json
import subprocess

from .triggers import msg_triggers
from .triggers import new_member_triggers

from .triggers.quack import quack
from .triggers.emoji_mode import invalid_emoji_message

from . import logging


class DuckClient(discord.Client):
    def __init__(
        self,
        config_filename="config/config.json",
        logging_filename="config/logging.json",
        messages_filename="config/messages.json",
        quacks_filename="config/quacks.txt",
    ):
        super().__init__()

        self.config_filename = (
            config_filename
        )  # TODO: remove this once emoji mode uses the database

        self.logging_filename = (
            logging_filename
        )  # TODO: remove this once logging uses the database

        with open(config_filename, "r") as config_file:
            self.config = json.load(config_file)
        with open(logging_filename, "r") as logging_file:
            self.logging = json.load(logging_file)
        with open(messages_filename, "r") as messages_file:
            self.messages = json.load(messages_file)
        with open(quacks_filename, "r") as quacks_file:
            self.quacks = quacks_file.read().split("\n%\n")

    async def on_ready(self):
        if len(sys.argv) > 1:
            args = ["kill", "-9"]
            args.extend(sys.argv[1:])
            subprocess.call(args)
        print(f"Connected as {self.user}!")

    async def on_message(self, msg):
        await logging.log(self, msg)

        if msg.author.bot:
            return

        if await invalid_emoji_message(self, msg):
            return

        replied = False
        for trigger in msg_triggers:
            if await trigger.execute(self, msg):
                replied = True

        if not replied:
            await quack(self, msg)

    async def on_member_join(self, member):
        for trigger in new_member_triggers:
            await trigger.execute(self, member)
