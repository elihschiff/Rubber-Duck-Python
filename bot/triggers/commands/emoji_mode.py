from . import Command
from .. import utils


async def channel_in_emoji_state(client, channel, command):
    async with client.lock:
        client.c.execute(
            f"SELECT count(*) FROM {command}_channels WHERE channel_id = :channel_id",
            {"channel_id": channel.id},
        )
        hits = client.c.fetchone()[0]
        return hits > 0


async def user_in_emoji_state(client, user, command):
    async with client.lock:
        client.c.execute(
            f"SELECT count(*) FROM {command}_users WHERE user_id = :user_id",
            {"user_id": user.id},
        )
        hits = client.c.fetchone()[0]
        return hits > 0


class EmojiMode(Command):
    names = ["emoji", "unemoji"]
    description = "Modifies the state of (un)emoji-mode on an entity"
    requires_mod = True

    async def channel_emoji_mode_toggle(self, client, channel, command):
        if await channel_in_emoji_state(client, channel, command):
            await self.channel_emoji_mode_off(client, channel, command)
        else:
            await self.channel_emoji_mode_on(client, channel, command)

    async def channel_emoji_mode_on(self, client, channel, command):
        if await channel_in_emoji_state(client, channel, command):
            return

        async with client.lock:
            client.c.execute(
                f"INSERT INTO {command}_channels VALUES (:channel_id)",
                {"channel_id": channel.id},
            )
            client.connection.commit()

        await utils.delay_send(
            channel,
            client.messages[f"{command}_mode_channel_activate"],
            delay_factor=0.01,
        )

    async def channel_emoji_mode_off(self, client, channel, command):
        if not await channel_in_emoji_state(client, channel, command):
            return

        async with client.lock:
            client.c.execute(
                f"DELETE FROM {command}_channels WHERE channel_id = :chann_id",
                {"chann_id": channel.id},
            )
            client.connection.commit()

        await utils.delay_send(
            channel,
            client.messages[f"{command}_mode_channel_deactivate"],
            delay_factor=0.01,
        )

    async def user_emoji_mode_toggle(self, client, user, sending_channel, command):
        if await user_in_emoji_state(client, user, command):
            await self.user_emoji_mode_off(client, user, sending_channel, command)
        else:
            await self.user_emoji_mode_on(client, user, sending_channel, command)

    async def user_emoji_mode_on(self, client, user, sending_channel, command):
        if await user_in_emoji_state(client, user, command):
            return

        async with client.lock:
            client.c.execute(
                f"INSERT INTO {command}_users VALUES (:user_id)", {"user_id": user.id}
            )
            client.connection.commit()

        try:
            await user.send(client.messages[f"{command}_mode_user_activate"])
        except HTTPException:
            pass

        await sending_channel.send(
            client.messages[f"{command}_mode_user_activate_public"].format(user.mention)
        )

    async def user_emoji_mode_off(self, client, user, sending_channel, command):
        if not await user_in_emoji_state(client, user, command):
            return

        async with client.lock:
            client.c.execute(
                f"DELETE FROM {command}_users WHERE user_id = :usr_id",
                {"usr_id": user.id},
            )
            client.connection.commit()

        try:
            await user.send(client.messages[f"{command}_mode_user_deactivate"])
        except (HTTPException, discord.errors.Traceback):
            pass

        await sending_channel.send(
            client.messages[f"{command}_mode_user_deactivate_public"].format(
                user.mention
            )
        )

    async def execute_command(self, client, msg, content, **kwargs):
        if content == "":
            await self.channel_emoji_mode_toggle(client, msg.channel)
            return

        content = msg.content.split(" ")
        command = content[0][1:]
        subcommand = content[1]
        users = [
            client.SERVER.get_member(user_id)
            for user_id in msg.raw_mentions
            if client.SERVER.get_member(user_id) is not None
        ]
        channels = [
            client.SERVER.get_channel(channel_id)
            for channel_id in msg.raw_channel_mentions
            if client.SERVER.get_channel(channel_id) is not None
        ]

        if subcommand == "on":
            for user in users:
                await self.user_emoji_mode_on(client, user, msg.channel, command)
            for channel in channels:
                await self.channel_emoji_mode_on(client, channel, command)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_on(client, msg.channel, command)

        elif subcommand == "off":
            for user in users:
                await self.user_emoji_mode_off(client, user, msg.channel, command)
            for channel in channels:
                await self.channel_emoji_mode_off(client, channel, command)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_off(client, msg.channel, command)

        else:
            for user in users:
                await self.user_emoji_mode_toggle(client, user, msg.channel, command)
            for channel in channels:
                await self.channel_emoji_mode_toggle(client, channel, command)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_toggle(client, msg.channel, command)
