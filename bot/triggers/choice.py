from .. import utils
import random


def load(bot):
    usage = "!choice choice1 choice2"

    @bot.command(
        aliases=["choose"], help="Chooses from a list of things", usage=usage,
    )
    async def choice(ctx):
        choices = ctx.message.clean_content.split()[1:]
        if not choices:
            await ctx.send(f"Usage: `{usage}`")
            return

        async with ctx.typing():
            choice = utils.sanitize(random.choice(choices))
            await utils.delay_send(ctx.channel, f"`{choice}`")
