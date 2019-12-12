def load(bot):
    @bot.command(
        aliases=["academicintegrity", "academic_integrity"],
        help="Reminds the channel about RPI's academic integrity policy",
    )
    async def ai(ctx):
        await ctx.send(ctx.bot.messages["academic_integrity"])
