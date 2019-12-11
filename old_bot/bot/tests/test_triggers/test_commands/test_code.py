import unittest
import json
from ... import test_utils
from ....duck import DuckClient


class TestCode(unittest.TestCase):
    def setUp(self):
        with open("config/messages.json", "r") as messages_file:
            messages = json.load(messages_file)
            self.code_message = messages["code"]
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_code(self):
        msg = test_utils.init_message(f"!code")
        await self.client.on_message(msg)
        self.assertEqual(msg.channel.test_result, self.code_message)
        self.assertIsNone(msg.channel.embed_dict)
        self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_code_from_bot(self):
        msg = test_utils.init_message(f"!code")
        msg.author.bot = True
        await self.client.on_message(msg)
        self.assertIsNone(msg.channel.test_result)
        self.assertIsNone(msg.channel.embed_dict)
        self.assertIsNone(msg.channel.filename)
