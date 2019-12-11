import unittest
from ... import test_utils
from ....duck import DuckClient


class TestInvalidCommand(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_invalid_command(self):
        test_strings = ["askdbc", "kasjdvkjdsbv", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!{string}")
            await self.client.on_message(msg)
            self.assertEqual(
                msg.channel.test_result,
                self.client.messages["invalid_command"].format(f"!{string}"),
            )
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_invalid_command_from_bot(self):
        test_strings = ["askdbc", "kasjdvkjdsbv", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!{string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_not_invalid_command(self):
        test_strings = ["abcd", "!"]
        for string in test_strings:
            msg = test_utils.init_message(string)
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)
