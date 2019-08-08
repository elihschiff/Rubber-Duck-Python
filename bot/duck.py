import sys
import discord
import json
import subprocess

from .triggers import msg_triggers
from .triggers import new_member_triggers
from .triggers import reaction_triggers

from .triggers.quack import quack


class DuckClient(discord.Client):
    def __init__(
        self,
        config_filename="config/config.json",
        messages_filename="config/messages.json",
        quacks_filename="config/quacks.txt",
    ):
        super().__init__()

        with open(config_filename, "r") as config_file:
            self.config = json.load(config_file)
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
        if msg.author.bot:
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

    # async def on_raw_reaction_add(self, payload):
    #     discord.TextChannel(id=payload.channel_id).get_message(payload.message_id)

    async def on_reaction_add(self, reaction, usr):
        for trigger in reaction_triggers:
            await trigger.execute(self, reaction, usr)
