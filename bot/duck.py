import asyncio
import json
import subprocess
import sqlite3
import sys

import discord

from . import logging
from .triggers import utils
from .triggers import msg_triggers, new_member_triggers, reaction_triggers
from .triggers.commands import invalid_command
from .triggers.quack import quack
from .triggers.emoji_mode import invalid_emoji_message


class DuckClient(discord.Client):
    def __init__(
        self,
        config_filename="config/config.json",
        roles_filename="config/roles.json",
        messages_filename="config/messages.json",
        quacks_filename="config/quacks.txt",
        games_filename="config/games.txt",
        path=sys.path[0] + "/",
    ):
        super().__init__()
        config_filename = path + config_filename
        roles_filename = path + roles_filename
        messages_filename = path + messages_filename
        quacks_filename = path + quacks_filename
        games_filename = path + games_filename
        with open(config_filename, "r") as config_file:
            self.config = json.load(config_file)
        with open(roles_filename, "r") as roles_file:
            self.roles = json.load(roles_file)
        with open(messages_filename, "r") as messages_file:
            self.messages = json.load(messages_file)
        with open(quacks_filename, "r") as quacks_file:
            self.quacks = quacks_file.read().split("\n%\n")
        with open(games_filename, "r") as games_file:
            self.game_footers = games_file.read().split("\n%\n")

        if self.config["ENABLE_COURSES"]:
            self.messages["remove_hidden_role_public"] = "DMed!"
            self.messages["add_hidden_role_public"] = "DMed!"
        else:
            self.messages["remove_hidden_role_public"] = self.messages[
                "remove_no_roles_match"
            ]
            self.messages["add_hidden_role_public"] = self.messages[
                "add_no_roles_match"
            ]

        self.lock = asyncio.Lock()
        self.connection = sqlite3.connect(path + "database.db")
        self.c = self.connection.cursor()

        self.log_lock = asyncio.Lock()
        self.log_connection = sqlite3.connect(path + "logging.db")
        self.log_c = self.log_connection.cursor()

    async def on_ready(self):
        if len(sys.argv) > 1:
            args = ["kill", "-9"]
            args.extend(sys.argv[1:])
            subprocess.call(args)

        self.LOG_SERVER = self.get_guild(self.config["LOG_SERVER_ID"])
        self.SERVER = self.get_guild(self.config["SERVER_ID"])

        try:
            traceback_server = self.get_guild(self.config["TRACEBACK_SERVER_ID"])
            self.TRACEBACK_CHANNEL = traceback_server.get_channel(
                self.config["TRACEBACK_CHANNEL_ID"]
            )
        except:
            self.TRACEBACK_CHANNEL = None

        print(f"Connected as {self.user}!")

    async def on_message(self, msg):
        try:
            await logging.log_message(self, msg)
        except AttributeError:
            pass
        except Exception as e:
            await utils.sendTraceback(self, msg.content)

        if msg.author.bot or utils.user_in_timeout(self, msg.author):
            return

        if await invalid_emoji_message(self, msg):
            return

        replied = False
        best_trigger = None
        best_trigger_idx = 0
        best_trigger_score = self.config["min_trigger_fuzzy_score"]
        for trigger in msg_triggers:
            if type(trigger).__name__ in self.config["disabled_triggers"]["msg"]:
                continue
            try:
                trigger_score, idx = await trigger.get_trigger_score(self, msg)
                if trigger_score > best_trigger_score:
                    best_trigger = trigger
                    best_trigger_score = trigger_score
                    best_trigger_idx = idx
                if trigger_score == 1:
                    await trigger.execute_message(self, msg, idx)
                    replied = True
            except Exception as e:
                await utils.sendTraceback(self, msg.content)
                replied = True

        if best_trigger and replied == False:
            await best_trigger.execute_message(self, msg, best_trigger_idx)
            replied = True

        if not replied:
            if not await invalid_command(self, msg):
                await quack(self, msg)

    async def on_raw_message_edit(self, msg):
        channel = await self.fetch_channel(msg.data["channel_id"])
        msg_full = await channel.fetch_message(msg.message_id)
        user = await self.fetch_user(msg_full.author.id)

        if user.bot:
            return
        try:
            await logging.log_message(self, msg_full, "(EDITED)")
            await invalid_emoji_message(self, msg_full)
        except AttributeError:
            pass

    async def on_raw_message_delete(self, msg):
        try:
            await logging.log_message_delete(self, msg)
        except AttributeError:
            pass

    async def on_member_join(self, member):
        for trigger in new_member_triggers:
            if type(trigger).__name__ in self.config["disabled_triggers"]["new_member"]:
                continue

            try:
                await trigger.execute_new_member(self, member)
            except Exception as e:
                await utils.sendTraceback(self)

    async def on_raw_reaction_add(self, reaction):
        user = self.SERVER.get_member(reaction.user_id)
        if not user:  # user is not in the cache
            user = await self.fetch_user(reaction.user_id)

        # This may need to be removed later but for now we dont every do anything
        # when a bot sending the reaction so this saves up to 2 api calls
        if user.bot:
            return

        channel = self.get_channel(reaction.channel_id)
        if not channel:  # channel is not in the cache
            channel = await self.fetch_channel(reaction.channel_id)

        # as far as I know there is not get_message command that checks the cache
        msg = await channel.fetch_message(reaction.message_id)

        for trigger in reaction_triggers:
            if type(trigger).__name__ in self.config["disabled_triggers"]["reaction"]:
                continue

            try:
                result = await trigger.execute_reaction(
                    self, reaction, channel, msg, user
                )
                # if you delete the message reacted to, return False
                if result is False:
                    break
            except Exception as e:
                await utils.sendTraceback(self)
