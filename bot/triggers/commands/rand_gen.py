from . import Command
from .. import utils
import random


class RandomGen(Command):
    names = ["random", "rand"]
    description = "Returns a random float or int with specified parameters.  Calling !random int will throw a number between 1 and 6"
    needsContent = False

    async def execute_command(self, client, msg, content):
        args = content.split()

        # No args
        if len(content) == 0:
            await utils.delay_send(msg.channel, str(random.random()))

        elif args[0] == "int":

            # Simulates a dice roll by default
            if len(args) == 1:
                await utils.delay_send(msg.channel, str(random.randint(1, 6)))

            elif len(args) == 3:

                if int(args[1]) > int(args[2]):
                    await utils.delay_send(
                        msg.channel,
                        "ERROR: argument 1 must be less than or equal to argument 2\n",
                    )

                else:
                    await utils.delay_send(
                        msg.channel, str(random.randint(int(args[1]), int(args[2])))
                    )

            else:
                await utils.delay_send(
                    msg.channel, "ERROR: Please specify two ints `a, b` where `a < b`\n"
                )
