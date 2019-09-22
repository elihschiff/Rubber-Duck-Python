import sys
import discord
from discord import ChannelType
import json
import subprocess
import threading
import sqlite3
import traceback

from .triggers import msg_triggers, new_member_triggers, reaction_triggers

from .triggers.commands import invalid_command

from .triggers.quack import quack
from .triggers.emoji_mode import invalid_emoji_message

from . import logging


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

        self.lock = threading.Lock()
        self.connection = sqlite3.connect("database.db")
        self.c = self.connection.cursor()

        self.log_lock = threading.Lock()
        self.log_connection = sqlite3.connect("logging.db")
        self.log_c = self.log_connection.cursor()

    async def on_ready(self):
        if len(sys.argv) > 1:
            args = ["kill", "-9"]
            args.extend(sys.argv[1:])
            subprocess.call(args)
        self.SERVER = self.get_guild(self.config["SERVER_ID"])

        try:
            traceback_server = self.get_guild(self.config["TRACEBACK_SERVER_ID"])
            self.TRACEBACK_CHANNEL = traceback_server.get_channel(
                self.config["TRACEBACK_CHANNEL_ID"]
            )
        except:
            self.TRACEBACK_CHANNEL = None

        self.LOG_SERVER = self.get_guild(self.config["LOG_SERVER_ID"])

        print(f"Connected as {self.user}!")

    async def on_message(self, msg):
        try:
            await logging.log(self, msg)
        except:
            pass

        if msg.author.bot:
            return

        if await invalid_emoji_message(self, msg):
            return

        replied = False
        for trigger in msg_triggers:
            if type(trigger).__name__ in self.config["disabled_triggers"]["msg"]:
                continue
            try:
                if await trigger.execute_message(self, msg):
                    replied = True
            except Exception as e:
                await sendTraceback(self, msg.content)
                replied = True

        if not replied:
            if not await invalid_command(self, msg):
                await quack(self, msg)

    async def on_member_join(self, member):
        for trigger in new_member_triggers:
            if type(trigger).__name__ in self.config["disabled_triggers"]["new_member"]:
                continue

            try:
                await trigger.execute_new_member(self, member)
            except Exception as e:
                await sendTraceback(self)

    async def on_raw_reaction_add(self, reaction):
        for trigger in reaction_triggers:
            if type(trigger).__name__ in self.config["disabled_triggers"]["reaction"]:
                continue

            try:
                await trigger.execute_reaction(self, reaction)
            except Exception as e:
                await sendTraceback(self)


# prints a traceback and sends it to discord
async def sendTraceback(client, content=""):
    # print the traceback to the terminal
    print(traceback.format_exc())

    # if there is a traceback server and channel, send the traceback in discord as well
    try:
        msg_to_send = f"```bash\n{traceback.format_exc()}\n```"
        if content:
            msg_to_send = f"`{content}`\n" + msg_to_send
        await client.TRACEBACK_CHANNEL.send(msg_to_send)
    except:
        print(
            "\nNote: traceback was not sent to Discord, if you want this double check your config.json"
        )
