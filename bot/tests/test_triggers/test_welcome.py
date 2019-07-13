import unittest
import json
import discord
from .. import test_utils
from ...duck import DuckClient


class TestWelcome(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        with open("config/config.json", "r") as config_file:
            config = json.load(config_file)
            self.welcome_channel_id = config["welcome_channel_id"]
        with open("config/messages.json", "r") as messages_file:
            messages = json.load(messages_file)
            self.welcome_message = messages["welcome"]

    @test_utils.async_test
    async def test_welcome_public(self):
        user = test_utils.MockUser()

        channel = test_utils.MockChannel()
        channel.id = self.welcome_channel_id
        user.guild = channel.guild

        user.guild.channels[self.welcome_channel_id] = channel

        await self.client.on_member_join(user)

        self.assertEqual(channel.test_result, self.welcome_message.format(user.mention))
