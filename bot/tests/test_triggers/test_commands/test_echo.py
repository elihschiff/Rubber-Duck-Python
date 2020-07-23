import unittest
from ... import test_utils
from ....duck import DuckClient


class TestEcho(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_echo(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!echo {string}")
            await self.client.on_message(msg)
            self.assertEqual(msg.channel.test_result, string)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_echo_from_bot(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!echo {string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_echo_empty(self):
        for num_spaces in range(0, 1):
            msg = test_utils.init_message("!echo" + " " * num_spaces)
            await self.client.on_message(msg)
            self.assertEqual(
                msg.channel.test_result,
                self.client.messages["invalid_command"].format(f"!echo"),
            )
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)
