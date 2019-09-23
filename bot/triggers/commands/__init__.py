from ..message_trigger import MessageTrigger
import re


class Command(MessageTrigger):
    prefixes = ["!"]

    async def is_valid(self, msg) -> (int, bool):
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

        if self.needsContent and len(msg.content[len(command) :].strip()) == 0:
            return (None, True)

        try:
            if not await self.valid_command(msg):
                return (None, True)
        except:
            pass

        return (len(command), True)

    async def execute_message(self, client, msg) -> bool:
        (idx, recognized) = await self.is_valid(msg)
        if idx is not None:
            await self.execute_command(client, msg, msg.clean_content[idx:].strip())
        return recognized

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")

    def __lt__(self, other):
        return self.names[0] < other.names[0]


from .ai import AI
from .class_management import AddClass, RemoveClass
from .code import Code
from .echo import Echo
from .emoji_mode import EmojiMode
from .games import ConnectFour
from .latex import Latex  # latex machine broke
from .list_classes import ListClasses
from .lmdtfy import Lmdtfy, Lmgtfy
from .man import Man
from .math import Math
from .minecraft import Minecraft
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
    Code(),
    ConnectFour(),
    Echo(),
    EmojiMode(),
    Latex(),  # latex machine broke
    ListClasses(),
    Lmdtfy(),
    Lmgtfy(),
    Man(),
    Math(),
    # Minecraft(),
    RemoveClass(),
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

    cleaned_content = msg.content.replace("`", "'")

    await msg.channel.send(client.messages["invalid_command"].format(cleaned_content))
    return True
