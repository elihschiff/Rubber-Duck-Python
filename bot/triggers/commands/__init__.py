from ..message_trigger import MessageTrigger
from .. import utils
import re


class Command(MessageTrigger):
    prefixes = ["!"]

    async def is_valid(self, client, msg) -> (int, bool):
        command = ""

        for name in self.names:
            for prefix in self.prefixes:
                if re.match(f"^{prefix}{name}\\b", msg.content.lower()):
                    command = prefix + name
                    break
            if command:
                break

        if len(command) == 0:
            return (None, False)

        # checks if a trigger causes spam and then if that trigger should run given the channel it was sent in
        try:  # any command without self.causes_spam will cause an exception and skip this to run like normal
            if self.causes_spam:
                if msg.channel.id not in client.config["spam_channel_ids"]:
                    channel_tags = ""
                    for id in client.config["spam_channel_ids"]:
                        channel_tags += f" <#{id}>"
                    await utils.delay_send(
                        msg.channel,
                        client.messages["send_to_spam_channel"].format(channel_tags),
                    )
                    return (None, True)
        except:
            pass

        if self.needsContent and len(msg.content[len(command) :].strip()) == 0:
            return (None, True)

        try:
            if not await self.valid_command(client, msg):
                return (None, True)
        except:
            pass

        return (len(command), True)

    async def execute_message(self, client, msg) -> bool:
        (idx, recognized) = await self.is_valid(client, msg)
        if idx is not None:
            async with msg.channel.typing():
                await self.execute_command(client, msg, msg.clean_content[idx:].strip())
        return recognized

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")

    def __lt__(self, other):
        return self.names[0] < other.names[0]


from .ai import AI
from .choice import Choice
from .class_management import AddClass, RemoveClass
from .code import Code
from .connectfour import ConnectFour
from .cpp_ref import CppRef
from .dining import Dining
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
from .minecraft import Minecraft
from .poll import Poll
from .rand import Random
from .rgb import RGB
from .rps import RockPaperScissors
from .steam import Steam
from .tictactoe import TicTacToe
from .translate import Translate
from .uptime import Uptime
from .version import Version
from .wikipedia import Wikipedia
from .xkcd import Xkcd

# Commands will auto alphabetize
all_commands = [
    AddClass(),
    AI(),
    Choice(),
    Code(),
    ConnectFour(),
    CppRef(),
    Dining(),
    Echo(),
    EmojiMode(),
    Java(),
    Issue(),
    Latex(),  # latex machine broke
    ListClasses(),
    Lmdtfy(),
    Lmgtfy(),
    Man(),
    Math(),
    Minesweeper(),
    # Minecraft(),
    Poll(),
    Random(),
    RemoveClass(),
    RGB(),
    RockPaperScissors(),
    Steam(),
    TicTacToe(),
    Translate(),
    Uptime(),
    Version(),
    Wikipedia(),
    Xkcd(),
]
all_commands.sort()


async def invalid_command(client, msg):
    if msg.author.bot or len(msg.content) < 2 or msg.content[0] != "!":
        return False

    cleaned_content = msg.content.replace("`", "'")

    await msg.channel.send(client.messages["invalid_command"].format(cleaned_content))
    return True
