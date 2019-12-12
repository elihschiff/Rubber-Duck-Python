from .. import utils
from discord.ext.commands import UserInputError
import random
import typing


def load(bot):
    usage = "!random (optional int/float) num1 num2"

    @bot.command(
        aliases=["random"],
        help="Returns a random float or integer within the specified range",
        usage=usage,
    )
    async def rand(
        # Note: This is rand() instead of random() to avoid conflicts with the library
        ctx,
        arg1: typing.Union[int, float],
        arg2: typing.Union[int, float],
    ):
        if isinstance(arg1, int) and isinstance(arg2, int):
            output = random.randint(min(arg1, arg2), max(arg1, arg2))
        else:
            output = random.uniform(min(arg1, arg2), max(arg1, arg2))

        async with ctx.typing():
            await utils.delay_send(ctx.channel, str(output))

    @rand.error
    async def rand_error(ctx, error):
        if isinstance(error, UserInputError):
            await ctx.send(f"Usage: `{usage}`")
        else:
            raise error
