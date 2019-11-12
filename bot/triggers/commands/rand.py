from . import Command
from .. import utils
import random


class Random(Command):
    names = ["random", "rand"]
    description = "Returns a random float or integer with specified parameters"
    description2 = """**Description:** Returns a random float or integer with specified parameters
                      **Usage:** !random or !random (optional int/float) num1 num2
                      **Example:** !random, !random 1 10, !random float 1 10
                      **Alternate names:** !rand"""

    needsContent = False

    async def execute_command(self, client, msg, content):
        if len(content) == 0:
            await utils.delay_send(msg.channel, str(random.random()))
            return

        args = content.split()

        try:
            if len(args) == 2:
                arg1 = int(args[0])
                arg2 = int(args[1])
                random_val = random.randint(min(arg1, arg2), max(arg1, arg2))
                await utils.delay_send(msg.channel, str(random_val))
            elif args[0].lower() == "int":
                arg1 = int(args[1])
                arg2 = int(args[2])
                random_val = random.randint(min(arg1, arg2), max(arg1, arg2))
                await utils.delay_send(msg.channel, str(random_val))
            else:
                arg1 = float(args[1])
                arg2 = float(args[2])
                random_val = random.uniform(min(arg1, arg2), max(arg1, arg2))
                await utils.delay_send(msg.channel, str(random_val))
        except (ValueError, IndexError):
            await msg.channel.send("USAGE: `!random (int/float) num1 num2`")
