from bot.triggers.commands import Command


class Poll(Command):
    names = ["poll"]
    description = "Reacts with a thumbs up and thumbs down for polling on this message"
    usage = f"{prefixes[0]}poll [(optional) message]"
    examples = f"{prefixes[0]}poll, {prefixes[0]}poll ELi is better than Ben"

    async def execute_command(self, client, msg, content):
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
