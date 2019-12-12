# NOTE: To make the lives of future developers easier,
#       please keep these in alphabetical order

from . import ai, choice, issue, latex, random

all_commands = [ai, choice, issue, latex, random]


def load_cogs(bot):
    for command in all_commands:
        command.load(bot)
