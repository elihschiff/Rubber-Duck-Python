from . import Command
from .. import utils
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
        translated_text = translation.text

        content = content.replace("`", "'")

        translated_text = translated_text.replace("`", "'")

        response = f"`{content}` translates from {translation.src.upper()} to: `{translated_text}`"
        await utils.delay_send(msg.channel, response, 1)
