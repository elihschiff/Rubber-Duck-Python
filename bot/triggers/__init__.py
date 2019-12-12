from . import ai, choice

all_commands = [ai, choice]


def load_cogs(bot):
    for command in all_commands:
        command.load(bot)
