import unittest
from ... import test_utils
from ....duck import DuckClient


class TestTranslate(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_translate_one_message(self):
        test_strings = [
            ("我是一隻鴨子", '"我是一隻鴨子" translates from ZH-CN to: `I am a duck`'),
            (
                "אני ברווז גומי",
                '"אני ברווז גומי" translates from IW to: `I\'m a rubber duck`',
            ),
            (
                "Rwy'n robot hwyaden rwber",
                "\"Rwy'n robot hwyaden rwber\" translates from CY to: `I'm a rubber duck robot`",
            ),
            (
                "The rubber duck says quack",
                '"The rubber duck says quack" translates from EN to: `The rubber duck says quack`',
            ),
        ]
        for string in test_strings:
            msg = test_utils.init_message(f"!translate {string[0]}")
            await self.client.on_message(msg)
            self.assertEqual(msg.channel.test_result, string[1])
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_translate_multiple_messages(self):
        test_input = "我是一隻鴨子"
        expected_output = '"我是一隻鴨子" translates from ZH-CN to: `I was a duck`'

        msg = test_utils.init_message(test_input)
        msg2 = test_utils.init_message("!translate")
        msg2.channel = msg.channel
        msg2.id = 1
        msg2.channel.internal_history.append(msg2)

        await self.client.on_message(msg2)
        self.assertEqual(msg2.channel.test_result, expected_output)
        self.assertIsNone(msg.channel.embed_dict)
        self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_translate_one_message_from_bot(self):
        test_strings = [
            ("我是一隻鴨子", '"我是一隻鴨子" translates from ZH-CN to: `I was a duck`'),
            (
                "אני ברווז גומי",
                '"אני ברווז גומי" translates from IW to: `I\'m a rubber duck`',
            ),
            (
                "Rwy'n robot hwyaden rwber",
                "\"Rwy'n robot hwyaden rwber\" translates from CY to: `I'm a rubber duck robot`",
            ),
            (
                "The rubber duck says quack",
                '"The rubber duck says quack" translates from EN to: `The rubber duck says quack`',
            ),
        ]
        for string in test_strings:
            msg = test_utils.init_message(f"!translate {string[0]}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_translate_multiple_messages_from_bot(self):
        test_input = "我是一隻鴨子"
        expected_output = '"我是一隻鴨子" translates from ZH-CN to: `I was a duck`'

        msg = test_utils.init_message(test_input)
        msg2 = test_utils.init_message("!translate")
        msg2.channel = msg.channel
        msg2.id = 1
        msg2.channel.internal_history.append(msg2)
        msg2.author.bot = True

        await self.client.on_message(msg)
        self.assertIsNone(msg2.channel.test_result)
        self.assertIsNone(msg.channel.embed_dict)
        self.assertIsNone(msg.channel.filename)
