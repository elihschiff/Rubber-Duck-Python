from . import Command

import random
import nextcord

# Global game dictionary used amongst all games to keep track of memory usage
GLOBAL_GAMES = dict()


class Game(Command):
    causes_spam = True
    # get a randomized game footer
    def get_game_footer(self, client):
        return random.choice(client.game_footers)
