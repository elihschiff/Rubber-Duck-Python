from . import Command
from .. import utils
from ..utils import sanitized
from googletrans import Translator


class Translate(Command):
    names = ["translate"]
    description = "Translates a given phrase, or the previous message, into English"
    description2 = """**Description:** Translates a given phrase, or the previous message, into English
                      **Usage:** !translate [(optional) message]
                      **Example:** !translate, !translate hi
                      (If given no content, the command translates the previous message.)"""
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

        response = f"`{sanitized(content)}` translates from {translation.src.upper()} to: `{sanitized(translation.text)}`"
        await utils.delay_send(msg.channel, response, 1)
