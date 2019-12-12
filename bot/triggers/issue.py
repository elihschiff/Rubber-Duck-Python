from .. import utils


def load(bot):
    @bot.command(
        aliases=["issues"],
        help="Tells a user how to report an issue or request a change with the bot",
    )
    async def issue(ctx):
        await utils.delay_send(ctx.channel, ctx.bot.messages["issue"])
