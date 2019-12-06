from ..message_trigger import MessageTrigger
from .. import utils
from ..utils import sanitized
import re
from fuzzywuzzy import fuzz


class Command(MessageTrigger):
    prefixes = ["!"]

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

        if self.needsContent and len(msg.content[len(command) :].strip()) == 0:
            return (None, False)

        try:
            if not await self.valid_command(client, msg):
                return (None, False)
        except:
            pass

        if max_ratio != 1:
            return (None, max_ratio)

        return (len(command), True)

    async def get_trigger_score(self, client, msg):
        (idx, recognized) = await self.is_valid(client, msg)

        return recognized, idx

    async def execute_message(self, client, msg, idx):
        async with msg.channel.typing():
            # checks if a trigger causes spam and then if that trigger should run given the channel it was sent in
            try:  # any command without self.causes_spam will cause an exception and skip this to run like normal
                if self.causes_spam:
                    if msg.channel.id not in client.config["spam_channel_ids"]:
                        channel_tags = ""
                        for id in client.config["spam_channel_ids"]:
                            channel_tags += f" <#{id}>"
                        await utils.delay_send(
                            msg.channel,
                            client.messages["send_to_spam_channel"].format(
                                channel_tags
                            ),
                        )
                        return
            except:
                pass
            await self.execute_command(client, msg, msg.clean_content[idx:].strip())

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")

    def __lt__(self, other):
        return self.names[0] < other.names[0]


from .code import Code
from .connectfour import ConnectFour
from .emoji_mode import EmojiMode
from .lmdtfy import Lmdtfy, Lmgtfy
from .minesweeper import Minesweeper
from .rps import RockPaperScissors
from .tictactoe import TicTacToe

# Commands will auto alphabetize
all_commands = [
    Code(),
    ConnectFour(),
    EmojiMode(),
    Lmdtfy(),
    Lmgtfy(),
    Minesweeper(),
    RockPaperScissors(),
    TicTacToe(),
]
all_commands.sort()


async def invalid_command(client, msg):
    if msg.author.bot or len(msg.content) < 2 or msg.content[0] != "!":
        return False

    await msg.channel.send(
        client.messages["invalid_command"].format(sanitized(msg.content.strip()))
    )
    return True
