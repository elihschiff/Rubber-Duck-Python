import unittest
from urllib.parse import urlencode

from ... import test_utils
from ....duck import DuckClient


class TestLmdtfy(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_lmdtfy(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!lmdtfy {string}")
            await self.client.on_message(msg)
            url = "https://lmgtfy.com/?s=d&" + urlencode({"q": string})
            self.assertEqual(msg.channel.test_result, url)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_lmgtfy(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!lmgtfy {string}")
            await self.client.on_message(msg)
            url = "https://lmgtfy.com/?" + urlencode({"q": string})
            self.assertEqual(msg.channel.test_result, url)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_lmdtfy_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message(f"!lmdtfy" + " " * num_spaces)
            await self.client.on_message(msg)
            self.assertEqual(
                msg.channel.test_result,
                self.client.messages["invalid_command"].format(f"!lmdtfy"),
            )
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_lmgtfy_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message(f"!lmgtfy" + " " * num_spaces)
            await self.client.on_message(msg)
            self.assertEqual(
                msg.channel.test_result,
                self.client.messages["invalid_command"].format(f"!lmgtfy"),
            )
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_lmdtfy_from_bot(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!lmdtfy {string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_lmgtfy_from_bot(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!lmgtfy {string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)
