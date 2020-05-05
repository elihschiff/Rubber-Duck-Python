from googletrans import Translator

from . import Command
from .. import utils


class Translate(Command):
    names = ["translate"]
    description = "Translates a given phrase, or the previous message, into English"
    usage = "!translate [message]"
    examples = f"!translate いんちき"

    def __init__(self):
        self.translator = Translator()

    async def execute_command(self, client, msg, content):
        if len(content) == 0:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        translation = self.translator.translate(content)

        response = f"`{utils.sanitized(content)}` translates from {translation.src.upper()} to: `{utils.sanitized(translation.text)}`"
        await utils.delay_send(msg.channel, response, 1)
