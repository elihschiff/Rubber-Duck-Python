from . import Command


class Echo(Command):
    name = "echo"

    async def execute_command(self, msg, content):
        await msg.channel.send(content)
