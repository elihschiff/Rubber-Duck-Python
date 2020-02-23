from . import Command
from .. import utils
import random


class Random(Command):
    names = ["random", "rand"]
    description = "Returns a random float or integer with specified parameters"
    usage = "!random [(optional) int/float] [(optional) num1] [(optional) num2]"
    examples = f"!random, !random 1 10, !random float 1 10"
    notes = "By default, this returns a float in the range [0,1).  If given arguments, it'll try to match the type of the argument"

    async def execute_command(self, client, msg, content):
        if len(content) == 0:
            await utils.delay_send(msg.channel, str(random.random()))
            return

        args = content.split()

        try:
            if len(args) == 2:
                try:
                    arg1 = int(args[0])
                    arg2 = int(args[1])
                    random_val = random.randint(min(arg1, arg2), max(arg1, arg2))
                    await utils.delay_send(msg.channel, str(random_val))
                except ValueError:
                    arg1 = float(args[0])
                    arg2 = float(args[1])
                    random_val = random.uniform(min(arg1, arg2), max(arg1, arg2))
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
