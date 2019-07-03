from discord.ext import commands


@commands.command()
async def echo(ctx, *, message):
    await ctx.send(message)
