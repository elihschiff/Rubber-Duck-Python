from ..message_trigger import MessageTrigger
from .. import utils
import re
from fuzzywuzzy import fuzz

from discord import ChannelType


class Command(MessageTrigger):
    prefixes = ["!"]
    requires_mod = False
    should_type = True

    async def is_valid(self, client, msg) -> (int, bool):
        command = ""

        max_ratio = 0
        for name in self.names:
            for prefix in self.prefixes:
                if re.match(f"^{prefix}{name}\\b", msg.content.lower()):
                    command = prefix + name
                    max_ratio = 1  # exact match
                    break
                if msg.content.lower().startswith(prefix):
                    ratio = fuzz.ratio(
                        msg.content.lower().split()[0], f"{prefix}{name}"
                    )
                    max_ratio = ratio if ratio > max_ratio else max_ratio
            if command:
                break

        if command == "" and len(msg.content.lower()) > 0:
            command = msg.content.lower().split()[0]

        if max_ratio != 1:
            return (None, max_ratio)

        return (len(command), True)

    async def get_trigger_score(self, client, msg):
        (idx, recognized) = await self.is_valid(client, msg)

        return recognized, idx

    async def execute_message(self, client, msg, idx):
        if self.requires_mod and not utils.user_is_mod(client, msg.author):
            await utils.delay_send(msg.channel, client.messages["invalid_permissions"])
            return
        # checks if a trigger causes spam and then if that trigger should run given the channel it was sent in
        try:  # any command without self.causes_spam will cause an exception and skip this to run like normal
            if self.causes_spam and msg.channel.type is not ChannelType.private:
                if msg.channel.id not in client.config["spam_channel_ids"]:
                    channel_tags = ""
                    for id in client.config["spam_channel_ids"]:
                        channel_tags += f" <#{id}>"
                    await utils.delay_send(
                        msg.channel,
                        client.messages["send_to_spam_channel"].format(channel_tags),
                    )
                    return
        except:
            pass

        # The execute command is defined here to decrease code reuse below
        async def _execute():
            await self.execute_command(
                client, msg, utils.sanitized(msg.clean_content[idx:].strip())
            )

        if self.should_type:
            async with msg.channel.typing():
                await _execute()
        else:
            await _execute()

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")

    def __lt__(self, other):
        return self.names[0] < other.names[0]


from .ai import AI
from .anime import Anime
from .choice import Choice
from .class_management import AddClass, RemoveClass
from .code import Code
from .connectfour import ConnectFour
from .cpp_ref import CppRef
from .delete import Delete
from .echo import Echo
from .emoji_mode import EmojiMode
from .java import Java
from .issue import Issue
from .latex import Latex  # latex machine broke
from .list_classes import ListClasses
from .lmdtfy import Lmdtfy, Lmgtfy
from .man import Man
from .math import Math
from .minesweeper import Minesweeper
from .poll import Poll
from .rand import Random
from .rgb import RGB
from .rps import RockPaperScissors
from .steam import Steam
from .tictactoe import TicTacToe
from .translate import Translate
from .version import Version
from .wikipedia import Wikipedia
from .xkcd import Xkcd

# Commands will auto alphabetize
all_commands = [
    AddClass(),
    AI(),
    Anime(),
    Choice(),
    Code(),
    ConnectFour(),
    CppRef(),
    Delete(),
    Echo(),
    EmojiMode(),
    Java(),
    Issue(),
    Latex(),
    ListClasses(),
    Lmdtfy(),
    Lmgtfy(),
    Man(),
    Math(),
    Minesweeper(),
    Poll(),
    Random(),
    RemoveClass(),
    RGB(),
    RockPaperScissors(),
    Steam(),
    TicTacToe(),
    Translate(),
    Version(),
    Wikipedia(),
    Xkcd(),
]
all_commands.sort()


async def invalid_command(client, msg):
    if msg.author.bot or len(msg.content) < 2 or msg.content[0] != "!":
        return False

    await utils.delay_send(
        msg.channel,
        client.messages["invalid_command"].format(utils.sanitized(msg.content.strip())),
    )
    return True
