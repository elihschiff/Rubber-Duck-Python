from . import Command
from .. import utils
from ..utils import sanitized
from google_trans_new import google_translator


class Translate(Command):
    names = ["translate"]
    description = "Translates a given phrase, or the previous message, into English"
    usage = "!translate [message]"
    examples = "!translate いんちき"

    def __init__(self):
        self.translator = google_translator()

    async def execute_command(self, client, msg, content, **kwargs):
        if len(content) == 0:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        translation = self.translator.translate(content, lang_tgt="en")

        response = f"`{sanitized(content)}` translates from {self.translator.detect(content)[0].upper()} to: `{sanitized(translation)}`"
        await utils.delay_send(msg.channel, response, 1)
