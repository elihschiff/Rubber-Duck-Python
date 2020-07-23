import asyncio
import json
import subprocess
import sqlite3
import sys
from typing import cast, Optional

import discord

from . import logging
from .triggers import utils
from .triggers import MSG_TRIGGERS, NEW_MEMBER_TRIGGERS, REACTION_TRIGGERS
from .triggers.commands import invalid_command
from .triggers.quack import quack
from .triggers.emoji_mode import invalid_emoji_message


# pylint: disable=too-many-instance-attributes
class DuckClient(discord.Client):
    def __init__(self, root_path: str = sys.path[0] + "/"):
        super().__init__()

        config_filename = root_path + "config/config.json"
        roles_filename = root_path + "config/roles.json"
        messages_filename = root_path + "config/messages.json"
        quacks_filename = root_path + "config/quacks.txt"
        games_filename = root_path + "config/games.txt"

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
        self.connection = sqlite3.connect(root_path + "database.db")
        self.cursor = self.connection.cursor()

        self.log_lock = asyncio.Lock()
        self.log_connection = sqlite3.connect(root_path + "logging.db")
        self.log_c = self.log_connection.cursor()

        self.log_server = cast(discord.Guild, None)
        self.server = cast(discord.Guild, None)
        self.traceback_channel: Optional[discord.TextChannel] = None

    async def on_ready(self) -> None:
        if len(sys.argv) > 1:
            args = ["kill", "-9"]
            args.extend(sys.argv[1:])
            subprocess.call(args)

        self.log_server = cast(
            discord.Guild, self.get_guild(self.config["log_server_ID"])
        )
        self.server = cast(discord.Guild, self.get_guild(self.config["server_ID"]))

        try:
            traceback_server = cast(
                discord.Guild, self.get_guild(self.config["TRACEBACK_SERVER_ID"])
            )
            self.traceback_channel = cast(
                Optional[discord.TextChannel],
                traceback_server.get_channel(self.config["TRACEBACK_CHANNEL_ID"]),
            )
        except KeyError:
            self.traceback_channel = None

        print(f"Connected as {self.user}!")

    async def on_message(self, msg: discord.Message) -> None:
        try:
            await logging.log_message(self, msg)

            if msg.author.bot or utils.user_in_timeout(self, msg.author):
                return

            if await invalid_emoji_message(self, msg):
                return

            if (
                "discord.gg/" in msg.content
                or "discordapp.com/invite/" in msg.content
                or "discord.com/invite/" in msg.content
            ):
                await msg.delete()
                await msg.author.send(
                    f"Your message (`{utils.sanitized(msg.content)}`) has been removed because it contained a discord server invite link."
                )
                return

            replied = False
            best_trigger = None
            best_trigger_idx = None
            best_trigger_score = self.config["min_trigger_fuzzy_score"]
            for trigger in MSG_TRIGGERS:
                if type(trigger).__name__ in self.config["disabled_triggers"]["msg"]:
                    continue

                trigger_score, idx = await trigger.get_trigger_score(self, msg)
                if trigger_score > best_trigger_score:
                    best_trigger = trigger
                    best_trigger_score = trigger_score
                    best_trigger_idx = idx
                if trigger_score == 1:
                    idx = cast(int, idx)
                    await trigger.execute_message(self, msg, idx)
                    replied = True

            if best_trigger and not replied:
                best_trigger_idx = cast(int, best_trigger_idx)
                await best_trigger.execute_message(self, msg, best_trigger_idx)
                replied = True

            if not replied:
                if not await invalid_command(self, msg):
                    await quack(self, msg)
        # pylint: disable=bare-except
        except:
            await utils.send_traceback(self, msg.content)

    async def on_raw_message_edit(self, msg: discord.RawMessageUpdateEvent) -> None:
        try:
            channel = cast(
                utils.Sendable, await self.fetch_channel(msg.data["channel_id"])
            )
            msg_full = await channel.fetch_message(msg.message_id)
            user = await self.fetch_user(msg_full.author.id)

            if user.bot:
                return

            if (
                "discord.gg/" in msg_full.content
                or "discordapp.com/invite/" in msg_full.content
                or "discord.com/invite/" in msg_full.content
            ):
                await msg_full.delete()
                await msg_full.author.send(
                    f"Your message (`{utils.sanitized(msg_full.content)}`) has been removed because it contained a discord server invite link."
                )
                return

            await logging.log_message(self, msg_full, "(EDITED)")
            await invalid_emoji_message(self, msg_full)
        # pylint: disable=bare-except
        except:
            await utils.send_traceback(self, msg_full.content)

    async def on_raw_message_delete(self, msg: discord.RawMessageDeleteEvent) -> None:
        try:
            await logging.log_message_delete(self, msg)
        except AttributeError:
            pass

    async def on_member_join(self, member: discord.Member) -> None:
        for trigger in NEW_MEMBER_TRIGGERS:
            if type(trigger).__name__ in self.config["disabled_triggers"]["new_member"]:
                continue

            try:
                await trigger.execute_new_member(self, member)
            # pylint: disable=bare-except
            except:
                await utils.send_traceback(self)

    async def on_raw_reaction_add(
        self, reaction: discord.RawReactionActionEvent
    ) -> None:
        user = self.get_user(reaction.user_id)
        if not user:  # user is not in the cache
            user = await self.fetch_user(reaction.user_id)

        # This may need to be removed later but for now we dont every do anything
        # when a bot sending the reaction so this saves up to 2 api calls
        if user.bot:
            return

        channel = self.get_channel(reaction.channel_id)
        if not channel:  # channel is not in the cache
            channel = await self.fetch_channel(reaction.channel_id)
        channel = cast(discord.TextChannel, channel)

        # as far as I know there is not get_message command that checks the cache
        msg = await channel.fetch_message(reaction.message_id)

        for trigger in REACTION_TRIGGERS:
            if type(trigger).__name__ in self.config["disabled_triggers"]["reaction"]:
                continue

            try:
                result = await trigger.execute_reaction(
                    self, reaction, channel, msg, user
                )
                # if you delete the message reacted to, return False
                if result is False:
                    break
            # pylint: disable=bare-except
            except:
                await utils.send_traceback(self)
