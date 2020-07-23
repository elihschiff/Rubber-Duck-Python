import random
from typing import Any, Dict, FrozenSet

import discord

from . import Command
from ...duck import DuckClient

# Global game dictionary used amongst all games to keep track of memory usage
GLOBAL_GAMES: Dict[FrozenSet[str], Any] = dict()


def get_game_footer(client: DuckClient) -> str:
    return random.choice(client.game_footers)


class Game(Command):
    causes_spam = True
    # get a randomized game footer

    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        raise NotImplementedError("'execute_command' not implemented for this game")
