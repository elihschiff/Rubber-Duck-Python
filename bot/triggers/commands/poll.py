from bot.triggers.commands import Command


class Poll(Command):
    names = ["poll"]
    description = "Reacts with a thumbs up and thumbs down for polling on this message, or the previous message"
    needsContent = False

    async def execute_command(self, client, msg, content):
        if not content:
            async for message in msg.channel.history(limit=1, before=msg):
                msg = message

        await msg.add_reaction("👍")
        await msg.add_reaction("👎")
