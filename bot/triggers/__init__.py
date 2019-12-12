from . import ai

all_commands = [ai]


def load_cogs(bot):
    for command in all_commands:
        command.load(bot)
