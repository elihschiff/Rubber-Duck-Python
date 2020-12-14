from . import Command
from .. import utils
from ..utils import sanitized
from googletrans import Translator


class Translate(Command):
    names = ["translate"]
    description = "Translates a given phrase, or the previous message, into English"
    usage = "!translate [message]"
    examples = f"!translate いんちき"

    def __init__(self):
        self.translator = Translator()

    async def execute_command(self, client, msg, content, **kwargs):
        if len(content) == 0:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        translation = self.translator.translate(content)

        response = f"`{sanitized(content)}` translates from {translation.src.upper()} to: `{sanitized(translation.text)}`"
        await utils.delay_send(msg.channel, response, 1)
