from typing import cast, List

import discord

from . import Command
from .. import utils
from ...duck import DuckClient


async def channel_in_emoji_state(client: DuckClient, channel: utils.Sendable) -> bool:
    async with client.lock:
        client.cursor.execute(
            "SELECT count(*) FROM emoji_channels WHERE channel_id = :channel_id",
            {"channel_id": channel.id},
        )
        hits = client.cursor.fetchone()[0]
        return bool(hits > 0)


async def user_in_emoji_state(client: DuckClient, user: discord.Member) -> bool:
    async with client.lock:
        client.cursor.execute(
            "SELECT count(*) FROM emoji_users WHERE user_id = :user_id",
            {"user_id": user.id},
        )
        hits = client.cursor.fetchone()[0]
        return bool(hits > 0)


class EmojiMode(Command):
    names = ["emoji"]
    description = "Modifies the state of emoji-mode on an entity"
    requires_mod = True

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if content == "":
            await self.channel_emoji_mode_toggle(client, msg.channel)
            return

        action = content.split()[0]
        users = [
            cast(discord.Member, client.server.get_member(user_id))
            for user_id in msg.raw_mentions
            if client.server.get_member(user_id) is not None
        ]
        channels = [
            cast(discord.TextChannel, client.server.get_channel(channel_id))
            for channel_id in msg.raw_channel_mentions
            if client.server.get_channel(channel_id) is not None
        ]

        if action == "on":
            user_action = self.user_emoji_mode_on
            channel_action = self.channel_emoji_mode_on
        elif action == "off":
            user_action = self.user_emoji_mode_off
            channel_action = self.channel_emoji_mode_off
        else:
            user_action = self.user_emoji_mode_toggle
            channel_action = self.channel_emoji_mode_toggle

        for user in users:
            await user_action(client, user, msg.channel)
        for channel in channels:
            await channel_action(client, channel)

        if len(users) == 0 and len(channels) == 0:
            await channel_action(client, msg.channel)

    async def channel_emoji_mode_toggle(
        self, client: DuckClient, channel: utils.Sendable
    ) -> None:
        if await channel_in_emoji_state(client, channel):
            await self.channel_emoji_mode_off(client, channel)
        else:
            await self.channel_emoji_mode_on(client, channel)

    async def channel_emoji_mode_on(
        self, client: DuckClient, channel: utils.Sendable
    ) -> None:
        if await channel_in_emoji_state(client, channel):
            return

        async with client.lock:
            client.cursor.execute(
                "INSERT INTO emoji_channels VALUES (:channel_id)",
                {"channel_id": channel.id},
            )
            client.connection.commit()

        await utils.delay_send(
            channel, client.messages["emoji_mode_channel_activate"], delay_factor=0.01
        )

    async def channel_emoji_mode_off(
        self, client: DuckClient, channel: utils.Sendable
    ) -> None:
        if not await channel_in_emoji_state(client, channel):
            return

        async with client.lock:
            client.cursor.execute(
                "DELETE FROM emoji_channels WHERE channel_id = :chann_id",
                {"chann_id": channel.id},
            )
            client.connection.commit()

        await utils.delay_send(
            channel, client.messages["emoji_mode_channel_deactivate"], delay_factor=0.01
        )

    async def user_emoji_mode_toggle(
        self, client: DuckClient, user: discord.Member, sending_channel: utils.Sendable,
    ) -> None:
        if await user_in_emoji_state(client, user):
            await self.user_emoji_mode_off(client, user, sending_channel)
        else:
            await self.user_emoji_mode_on(client, user, sending_channel)

    async def user_emoji_mode_on(
        self, client: DuckClient, user: discord.Member, sending_channel: utils.Sendable,
    ) -> None:
        if await user_in_emoji_state(client, user):
            return

        async with client.lock:
            client.cursor.execute(
                "INSERT INTO emoji_users VALUES (:user_id)", {"user_id": user.id}
            )
            client.connection.commit()

        try:
            await user.send(client.messages["emoji_mode_user_activate"])
        except discord.HTTPException:
            pass

        await sending_channel.send(
            client.messages["emoji_mode_user_activate_public"].format(user.mention)
        )

    async def user_emoji_mode_off(
        self, client: DuckClient, user: discord.Member, sending_channel: utils.Sendable,
    ) -> None:
        if not await user_in_emoji_state(client, user):
            return

        async with client.lock:
            client.cursor.execute(
                "DELETE FROM emoji_users WHERE user_id = :usr_id", {"usr_id": user.id}
            )
            client.connection.commit()

        try:
            await user.send(client.messages["emoji_mode_user_deactivate"])
        except discord.HTTPException:
            pass

        await sending_channel.send(
            client.messages["emoji_mode_user_deactivate_public"].format(user.mention)
        )
