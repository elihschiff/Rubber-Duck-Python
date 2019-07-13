import unittest
from ... import test_utils
from ....duck import DuckClient


class TestMan(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_man_valid(self):
        test_strings = [
            ("https://linux.die.net/man/1/free", "free"),
            ("https://linux.die.net/man/3/fgets", "fgets"),
            ("https://linux.die.net/man/3/free", "3 free"),
        ]
        for string in test_strings:
            msg = test_utils.init_message(f"!man {string[1]}")
            await self.client.on_message(msg)
            self.assertEqual(msg.channel.test_result, string[0])
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_man_invalid(self):
        test_strings = ["abcd", "2 echo", "3"]
        for string in test_strings:
            msg = test_utils.init_message(f"!man {string}")
            await self.client.on_message(msg)
            self.assertEqual(
                msg.channel.test_result, f"Could not find man page for `{string}`"
            )
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_man_empty(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message("!man" + " " * num_spaces)
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_man_valid_from_bot(self):
        test_strings = ["free", "fgets", "3 free"]
        for string in test_strings:
            msg = test_utils.init_message(f"!man {string[1]}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_man_invalid_from_bot(self):
        test_strings = ["abcd", "2 echo", "3"]
        for string in test_strings:
            msg = test_utils.init_message(f"!man {string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)
