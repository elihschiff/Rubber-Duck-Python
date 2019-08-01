import asyncio
import shutil


def async_test(f):
    def wrapper(*args, **kwargs):
        coro = asyncio.coroutine(f)
        future = coro(*args, **kwargs)
        loop = asyncio.get_event_loop()
        loop.run_until_complete(future)

    return wrapper


import discord


class MockTyping:
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return


class MockUserPermissions:
    def __init__(self):
        self.administrator = False


class MockUser:
    def __init__(self):
        self.bot = False
        self.id = 0
        self.display_name = ""
        self.was_mentioned = False
        self.guild = None
        self.guild_permissions = MockUserPermissions()

    def mentioned_in(self, msg):
        return (
            self.was_mentioned
        )  # can be changed if a more robust solution is needed

    @property
    def mention(self):
        return f"<@{self.id}>"


class MockGuild:
    def __init__(self):
        self.members = {}
        self.channels = {}

    def get_member(self, member_id):
        return self.members[member_id]

    def get_channel(self, channel_id):
        return self.channels[channel_id]


class MockChannel:
    def __init__(self):
        self.id = 0
        self.internal_history = []
        self.guild = MockGuild()
        self.type = None

        self.test_result = None
        self.embed_dict = None
        self.filename = None

    async def send(self, message="", file=None, embed=None):
        self.test_result = message
        if file is not None:
            fname = file.fp.name
            new_fname = f"{fname}_test"
            shutil.copyfile(fname, new_fname)
            self.filename = new_fname
            file.close()
        else:
            self.filename = None

        if embed is not None:
            self.embed_dict = embed.to_dict()

        msg = init_message(message)
        msg.channel = self
        self.internal_history.append(msg)

    def typing(self):
        return MockTyping()

    async def history(self, limit=0):
        if limit is None or limit > len(self.internal_history):
            limit = len(self.internal_history)

        for i in reversed(range(0, limit)):
            yield self.internal_history[i]


class MockMessage:
    def __init__(self):
        self.id = 0
        self.mentions = []


def init_message(content=""):
    message = MockMessage()
    message.author = MockUser()
    message.channel = MockChannel()
    message.channel.internal_history.append(message)
    message.content = content
    return message
