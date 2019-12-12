from . import ai, choice, random

all_commands = [ai, choice, random]


def load_cogs(bot):
    for command in all_commands:
        command.load(bot)
