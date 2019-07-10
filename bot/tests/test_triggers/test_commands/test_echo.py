import unittest
from ... import test_utils
from ....triggers.commands import echo


class TestEcho(unittest.TestCase):
    def setUp(self):
        self.echo = echo.Echo()

    @test_utils.async_test
    async def test_echo_with_content(self):
        test_strings = ["abcd", "hello world!", "הברווז אומר היי"]
        for string in test_strings:
            msg = test_utils.init_message(f"!echo {string}")
            self.assertTrue(
                await self.echo.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            self.assertEqual(msg.channel.test_result, string)

    @test_utils.async_test
    async def test_echo_without_content(self):
        for num_spaces in range(0, 10):
            msg = test_utils.init_message("!echo" + " " * num_spaces)
            self.assertFalse(
                await self.echo.execute(
                    None, msg
                )  # `client` is passed as None because it is never used
            )
            self.assertIsNone(msg.channel.test_result)
