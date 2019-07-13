import unittest
from unittest.mock import patch
import sys
from . import test_utils

from ..duck import DuckClient
from ..triggers import MessageTrigger, NewMemberTrigger
from ..triggers.commands import Command


class TestExceptions(unittest.TestCase):
    def test_missing_config_file(self):
        with self.assertRaises(OSError):
            DuckClient(config_filename="")

    def test_missing_messages_file(self):
        with self.assertRaises(OSError):
            DuckClient(messages_filename="")

    def test_missing_quacks_file(self):
        with self.assertRaises(OSError):
            DuckClient(quacks_filename="")

    @test_utils.async_test
    async def test_kill_prev(self):
        client = DuckClient()
        with patch.object(sys, "argv", ["", "1"]):
            await client.on_ready()
        self.assertTrue(True)

    @test_utils.async_test
    async def test_bot_msg(self):
        client = DuckClient()
        msg = test_utils.init_message()
        client.on_message(msg)

    @test_utils.async_test
    async def test_empty_message_trigger(self):
        trigger = MockMessageTrigger()
        with self.assertRaises(NotImplementedError):
            await trigger.execute(None, None)

    @test_utils.async_test
    async def test_empty_command_trigger(self):
        trigger = MockCommandTrigger()
        with self.assertRaises(NotImplementedError):
            await trigger.execute_command(None, None, "")

    @test_utils.async_test
    async def test_empty_new_member_trigger(self):
        trigger = MockNewMemberTrigger()
        with self.assertRaises(NotImplementedError):
            await trigger.execute(None, None)


class MockMessageTrigger(MessageTrigger):
    def __init__(self):
        pass


class MockCommandTrigger(Command):
    def __init__(self):
        pass


class MockNewMemberTrigger(NewMemberTrigger):
    def __init__(self):
        pass
