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
        if len(content) == 0 and msg.reference is not None:
            # If no content here, this might be sent as a reply to another message with a message to translate
            content = " ".join(msg.reference.content.split()[1:])

        if len(content) == 0:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}", reply_to=msg)
            return

        translation = self.translator.translate(content, lang_tgt="en")

        response = f"`{sanitized(content)}` translates from {self.translator.detect(content)[0].upper()} to: `{sanitized(translation)}`"
        await utils.delay_send(msg.channel, response, 1, reply_to=msg)
