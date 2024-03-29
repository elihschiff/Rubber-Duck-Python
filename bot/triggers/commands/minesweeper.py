from . import Command
from .. import utils

import math
import random


class Minesweeper(Command):
    names = ["ms", "mine", "minesweeper"]
    description = "Sends a minesweeper game"
    usage = "!ms [(optional) width] [(optional) height] [(optional) number of mines]"
    examples = "!ms, !ms 10 3, !ms 5 5 2"
    causes_spam = True
    show_in_help = True

    async def execute_command(self, client, msg, content, **kwargs):
        height = 8
        width = 8
        args = content.split()
        if len(args) >= 1 and args[0].isdigit():
            height = int(args[0])
            width = int(args[0])
        if len(args) >= 2 and args[1].isdigit():
            height = int(args[1])
        height = max(1, min(9, height))
        width = max(1, min(9, width))

        mineCount = math.ceil((width * height / 64) * 10)
        if len(args) >= 3 and args[2].isdigit():
            mineCount = max(0, min(width * height, int(args[2])))
        cells = [[0 for i in range(width)] for j in range(height)]

        i = 0
        while i < mineCount:
            x = random.randint(0, height - 1)
            y = random.randint(0, width - 1)
            if cells[x][y] == -1:
                continue
            cells[x][y] = -1

            for a in range(-1, 2):
                for b in range(-1, 2):
                    if not (
                        y + b > width - 1
                        or y + b < 0
                        or x + a > height - 1
                        or x + a < 0
                    ):
                        if cells[x + a][y + b] != -1:
                            cells[x + a][y + b] += 1
            i += 1

        num = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]
        output = f"There are ||{mineCount}|| mines\n"
        output_head_len = len(output)
        for i in range(height):
            for j in range(width):
                output += "||"
                if cells[i][j] == -1:
                    output += ":bomb:"
                else:
                    output += num[cells[i][j]]
                output += "||"
            output += "\n"

        if len(output) >= 2000:
            await utils.delay_send(
                msg.channel, client.messages["ms_too_large"], reply_to=msg
            )
        else:
            await utils.delay_send(msg.channel, output, reply_to=msg)
