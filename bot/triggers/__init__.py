# NOTE: To make the lives of future developers easier,
#       please keep these in alphabetical order

from . import ai, choice, issue, latex, lmdtfy, random

all_commands = [ai, choice, issue, latex, lmdtfy, random]


def load_cogs(bot):
    for command in all_commands:
        command.load(bot)
