import unittest
import json
import discord
from .. import test_utils
from ...duck import DuckClient


class TestQuack(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        with open("config/quacks.txt", "r") as quacks_file:
            self.quacks = quacks_file.read().split("\n%\n")
        with open("config/config.json", "r") as config_file:
            config = json.load(config_file)
            self.quack_channels = config["quack_channels"]

        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_quack_dm(self):
        msg = test_utils.init_message()
        msg.channel.type = discord.ChannelType.private
        self.client.user.was_mentioned = False

        await self.client.on_message(msg)

        self.assertIn(msg.channel.test_result, self.quacks)

    @test_utils.async_test
    async def test_quack_mentioned(self):
        msg = test_utils.init_message()
        msg.mentions.append(self.client.user)
        self.client.user.was_mentioned = True

        await self.client.on_message(msg)

        self.assertIn(msg.channel.test_result, self.quacks)

    @test_utils.async_test
    async def test_quack_in_channel(self):
        self.client.user.was_mentioned = False

        for channel in self.quack_channels:
            msg = test_utils.init_message()
            msg.channel.id = channel

            await self.client.on_message(msg)

            self.assertIn(msg.channel.test_result, self.quacks)
