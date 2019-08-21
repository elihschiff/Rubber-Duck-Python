from .message_trigger import MessageTrigger
from . import utils

import re

url_regex = r"\b(https?:\/\/)?(www\.)?([\da-z\.-]+)\.([a-z\.]{2,6})\/[\w \.-]+?\.pdf\b"


class PdfToPng(MessageTrigger):
    async def execute_message(self, client, msg) -> bool:
        url = re.search(url_regex, msg.content)

        if url:
            await msg.add_reaction("\u0039\u20E3")
