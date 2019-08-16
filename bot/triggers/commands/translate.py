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
            this_message = False
            async for message in msg.channel.history(limit=10):
                if this_message and not message.author.bot:
                    content = message.content
                    break
                if message.id == msg.id:
                    this_message = True

        translation = self.translator.translate(content)
        response = f'"{content}" translates from {translation.src.upper()} to: `{translation.text}`'
        await utils.delay_send(msg.channel, response, 1)
