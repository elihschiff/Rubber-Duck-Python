from . import Command
from .. import utils
import random


class Random(Command):
    names = ["random", "rand"]
    description = "Returns a random float or integer with specified parameters"
    usage = "!random [(optional) int/float] [(optional) num1] [(optional) num2]"
    examples = "!random, !random 1 10, !random float 1 10"
    notes = "By default, this returns a float in the range [0,1).  If given arguments, it'll try to match the type of the argument"

    async def execute_command(self, client, msg, content, **kwargs):
        if len(content) == 0:
            await utils.delay_send(msg.channel, str(random.random()), reply_to=msg)
            return

        args = content.split()

        if len(args) == 2:
            arg1_idx = 0
        else:
            arg1_idx = 1

        try:
            try:
                arg1 = int(args[arg1_idx])
                arg2 = int(args[arg1_idx + 1])
            except ValueError:
                arg1 = float(args[arg1_idx])
                arg2 = float(args[arg1_idx + 1])
        except (IndexError, ValueError) as e:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}", reply_to=msg)
            return

        min_val = min(arg1, arg2)
        max_val = max(arg1, arg2)

        if args[0] == "int":
            try:
                arg1 = int(arg1)
                arg2 = int(arg2)
            except ValueError:
                await utils.delay_send(
                    msg.channel,
                    "Error: `int` specified but non-integer arguments given",
                    reply_to=msg,
                )
                return

        # Only generate an integer if we're given integers
        if type(arg1) is int and args[0] != "float":
            random_val = random.randint(min_val, max_val)
        else:
            random_val = random.uniform(min_val, max_val)

        await utils.delay_send(msg.channel, str(random_val), reply_to=msg)
