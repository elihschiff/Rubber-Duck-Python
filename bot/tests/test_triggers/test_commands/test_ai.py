import unittest
import json
from ... import test_utils
from ....duck import DuckClient


class TestAI(unittest.TestCase):
    def setUp(self):
        with open("config/messages.json", "r") as messages_file:
            messages = json.load(messages_file)
            self.ai_message = messages["academic_integrity"]
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_ai(self):
        test_strings = ["ai", "academic integrity"]
        for string in test_strings:
            msg = test_utils.init_message(f"!{string}")
            await self.client.on_message(msg)
            self.assertEqual(msg.channel.test_result, self.ai_message)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_ai_from_bot(self):
        test_strings = ["ai", "academic integrity"]
        for string in test_strings:
            msg = test_utils.init_message(f"!{string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)
