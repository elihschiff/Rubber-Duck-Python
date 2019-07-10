import asyncio


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


import discord


class MockTyping:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return

    async def __aenter__(self):
        return self.__enter__()

    async def __aexit__(self, exc_type, exc, tb):
        return


class MockChannel:
    def __init__(self):
        self.test_result = None
        self.id = 0

    async def send(self, message):
        self.test_result = message

    def typing(self):
        return MockTyping()


class MockUser:
    def __init__(self):
        self.bot = False
        self.id = 0


class MockMessage:
    def __init__(self):
        self.id = 0


def init_message(content):
    message = MockMessage()
    message.author = MockUser()
    message.channel = MockChannel()
    message.content = content
    return message
