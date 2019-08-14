import json

from . import Command
from .. import utils


class EmojiMode(Command):
    names = ["emoji"]
    description = "Modifies the state of emoji-mode on an entity"
    needsContent = False
    required_roles = ["%"]  # TODO: use this

    async def channel_emoji_mode_toggle(self, client, channel):
        if channel.id in client.config["EMOJI_CHANNELS"]:
            await self.channel_emoji_mode_off(client, channel)
        else:
            await self.channel_emoji_mode_on(client, channel)

    async def channel_emoji_mode_on(self, client, channel):
        if channel.id in client.config["EMOJI_CHANNELS"]:
            return

        client.config["EMOJI_CHANNELS"].append(channel.id)
        with open(client.config_filename, "w") as config_file:
            json.dump(client.config, config_file, indent=4)
        await utils.delay_send(
            channel, client.messages["emoji_mode_channel_activate"], delay_factor=0.01
        )

    async def channel_emoji_mode_off(self, client, channel):
        if channel.id not in client.config["EMOJI_CHANNELS"]:
            return

        client.config["EMOJI_CHANNELS"].remove(channel.id)
        with open(client.config_filename, "w") as config_file:
            json.dump(client.config, config_file, indent=4)
        await utils.delay_send(
            channel, client.messages["emoji_mode_channel_deactivate"], delay_factor=0.01
        )

    async def user_emoji_mode_toggle(self, client, user):
        if user.id in client.config["EMOJI_USERS"]:
            await self.user_emoji_mode_off(client, user)
        else:
            await self.user_emoji_mode_on(client, user)

    async def user_emoji_mode_on(self, client, user):
        if user.id in client.config["EMOJI_USERS"]:
            return
        client.config["EMOJI_USERS"].append(user.id)
        with open(client.config_filename, "w") as config_file:
            json.dump(client.config, config_file, indent=4)
        await user.send(client.messages["emoji_mode_user_activate"])

    async def user_emoji_mode_off(self, client, user):
        if user.id not in client.config["EMOJI_USERS"]:
            return

        client.config["EMOJI_USERS"].remove(user.id)
        with open(client.config_filename, "w") as config_file:
            json.dump(client.config, config_file, indent=4)
        await user.send(client.messages["emoji_mode_user_deactivate"])

    async def valid_command(self, msg) -> bool:
        return utils.user_is_admin(msg.author)

    async def execute_command(self, client, msg, content):
        if content == "":
            await self.channel_emoji_mode_toggle(client, msg.channel)
            return

        content = content.split(" ")
        users = msg.mentions
        channels = msg.channel_mentions

        if content[0] == "on":
            for user in users:
                await self.user_emoji_mode_on(client, user)
            for channel in channels:
                await self.channel_emoji_mode_on(client, channel)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_on(client, msg.channel)

        elif content[0] == "off":
            for user in users:
                await self.user_emoji_mode_off(client, user)
            for channel in channels:
                await self.channel_emoji_mode_off(client, channel)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_off(client, msg.channel)

        else:
            for user in users:
                await self.user_emoji_mode_toggle(client, user)
            for channel in channels:
                await self.channel_emoji_mode_toggle(client, channel)

            if len(users) == 0 and len(channels) == 0:
                await self.channel_emoji_mode_toggle(client, msg.channel)
