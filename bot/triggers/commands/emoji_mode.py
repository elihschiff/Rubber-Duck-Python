import json

from . import Command
from .. import utils


async def channel_in_emoji_state(client, channel):
    async with client.lock:
        client.c.execute(
            f"SELECT count(*) FROM emoji_channels WHERE channel_id = {channel.id}"
        )
        hits = client.c.fetchone()[0]
        return hits > 0


async def user_in_emoji_state(client, user):
    async with client.lock:
        client.c.execute(f"SELECT count(*) FROM emoji_users WHERE user_id = {user.id}")
        hits = client.c.fetchone()[0]
        return hits > 0


class EmojiMode(Command):
    names = ["emoji"]
    description = ""  # "Modifies the state of emoji-mode on an entity"
    needsContent = False
    requires_mod = True

    async def channel_emoji_mode_toggle(self, client, channel):
        if await channel_in_emoji_state(client, channel):
            await self.channel_emoji_mode_off(client, channel)
        else:
            await self.channel_emoji_mode_on(client, channel)

    async def channel_emoji_mode_on(self, client, channel):
        if await channel_in_emoji_state(client, channel):
            return

        async with client.lock:
            client.c.execute(f"INSERT INTO emoji_channels VALUES ({channel.id})")
            client.connection.commit()

        await utils.delay_send(
            channel, client.messages["emoji_mode_channel_activate"], delay_factor=0.01
        )

    async def channel_emoji_mode_off(self, client, channel):
        if not await channel_in_emoji_state(client, channel):
            return

        async with client.lock:
            client.c.execute(
                f"DELETE FROM emoji_channels WHERE channel_id = {channel.id}"
            )
            client.connection.commit()

        await utils.delay_send(
            channel, client.messages["emoji_mode_channel_deactivate"], delay_factor=0.01
        )

    async def user_emoji_mode_toggle(self, client, user, sending_channel):
        if await user_in_emoji_state(client, user):
            await self.user_emoji_mode_off(client, user, sending_channel)
        else:
            await self.user_emoji_mode_on(client, user, sending_channel)

    async def user_emoji_mode_on(self, client, user, sending_channel):
        if await user_in_emoji_state(client, user):
            return

        async with client.lock:
            client.c.execute(f"INSERT INTO emoji_users VALUES ({user.id})")
            client.connection.commit()

        await user.send(client.messages["emoji_mode_user_activate"])
        await sending_channel.send(
            client.messages["emoji_mode_user_activate_public"].format(user.mention)
        )

    async def user_emoji_mode_off(self, client, user, sending_channel):
        if not await user_in_emoji_state(client, user):
            return

        async with client.lock:
            client.c.execute(f"DELETE FROM emoji_users WHERE user_id = {user.id}")
            client.connection.commit()

        await user.send(client.messages["emoji_mode_user_deactivate"])
        await sending_channel.send(
            client.messages["emoji_mode_user_deactivate_public"].format(user.mention)
        )

    async def execute_command(self, client, msg, content):
        if content == "":
            await self.channel_emoji_mode_toggle(client, msg.channel)
            return

        content = content.split(" ")
        users = msg.mentions
        channels = msg.channel_mentions

        if content[0] == "on":
            for user in users:
                await self.user_emoji_mode_on(client, user, msg.channel)
            for channel in channels:
                await self.channel_emoji_mode_on(client, channel)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_on(client, msg.channel)

        elif content[0] == "off":
            for user in users:
                await self.user_emoji_mode_off(client, user, msg.channel)
            for channel in channels:
                await self.channel_emoji_mode_off(client, channel)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_off(client, msg.channel)

        else:
            for user in users:
                await self.user_emoji_mode_toggle(client, user, msg.channel)
            for channel in channels:
                await self.channel_emoji_mode_toggle(client, channel)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_toggle(client, msg.channel)
