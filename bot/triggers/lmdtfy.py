from .. import utils
from urllib.parse import urlencode


def load(bot):
    @bot.command(
        aliases=["search"],
        help="Helps someone look something up on the superior search engine",
        usage="!lmdtfy Does water boil in space?",
    )
    async def lmdtfy(ctx, *args):
        async with ctx.typing():
            query = " ".join(args)
            url = "https://lmgtfy.com/?s=d&" + urlencode({"q": query})
            await utils.delay_send(ctx.channel, url)

    @bot.command(
        help="Helps someone look something up on the inferior search engine",
        usage="!lmgtfy Why does water boil in space?",
    )
    async def lmgtfy(ctx, *args):
        async with ctx.typing():
            query = " ".join(args)
            url = "https://lmgtfy.com/?" + urlencode({"q": query})
            await utils.delay_send(ctx.channel, url)
