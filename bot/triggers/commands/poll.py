from bot.triggers.commands import Command


class Poll(Command):
    names = ["poll"]
    description = "Reacts with a thumbs up and thumbs down for polling on this message"
    usage = "!poll [(optional) message]"
    examples = "!poll, !poll ELi is better than Ben"

    should_type = False

    async def execute_command(self, client, msg, content, **kwargs):
        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
