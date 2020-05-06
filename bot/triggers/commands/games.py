import random

from . import Command

# Global game dictionary used amongst all games to keep track of memory usage
GLOBAL_GAMES = dict()


def get_game_footer(client):
    return random.choice(client.game_footers)


class Game(Command):
    causes_spam = True
    # get a randomized game footer

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")
