from . import Command
from .. import utils
from googletrans import Translator


class Translate(Command):
    names = ["translate"]
    description = "Translates a given phrase, or the previous message, into English"
    needsContent = False

    def __init__(self):
        self.translator = Translator()

    async def execute_command(self, client, msg, content):
        if len(content) == 0:
            await msg.channel.send(
                "Translation of old messages has been temporarily disabled."
            )
            return
            async for message in msg.channel.history(limit=1, before=msg):
                content = message.content

        translation = self.translator.translate(content)
        response = f'"{content}" translates from {translation.src.upper()} to: `{translation.text}`'
        await utils.delay_send(msg.channel, response, 1)
