import math
import random

from . import Command
from .. import utils


class Minesweeper(Command):
    names = ["ms", "mine", "minesweeper"]
    description = "Sends a minesweeper game"
    usage = "!ms [(optional) width] [(optional) height] [(optional) number of mines]"
    examples = f"!ms, !ms 10 3, !ms 5 5 2"
    causes_spam = True

    async def execute_command(self, client, msg, content):
        height = 8
        width = 8
        args = content.split()
        if len(args) >= 1 and args[0].isdigit():
            height = int(args[0])
            width = int(args[0])
        if len(args) >= 2 and args[1].isdigit():
            height = int(args[1])
        height = max(1, min(20, height))
        width = max(1, min(20, width))

        mine_count = math.ceil((width * height / 64) * 10)
        if len(args) >= 3 and args[2].isdigit():
            mine_count = max(0, min(width * height, int(args[2])))
        cells = [[0 for i in range(width)] for j in range(height)]

        i = 0
        while i < mine_count:
            x = random.randint(0, height - 1)
            y = random.randint(0, width - 1)
            if cells[x][y] == -1:
                continue
            cells[x][y] = -1

            for x_off in range(-1, 2):
                for y_off in range(-1, 2):
                    if not (
                        y + y_off > width - 1
                        or y + y_off < 0
                        or x + x_off > height - 1
                        or x + x_off < 0
                    ):
                        if cells[x + x_off][y + y_off] != -1:
                            cells[x + x_off][y + y_off] += 1
            i += 1

        num = ["0⃣", "1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣"]
        output = f"There are ||{mine_count}|| mines\n"
        for i in range(height):
            for j in range(width):
                output += "||"
                if cells[i][j] == -1:
                    output += ":bomb:"
                else:
                    output += num[cells[i][j]]
                output += "||"
            output += "\n"

        # 11 is the max number of chars per cell
        # times every cell
        # plus a \n for each line
        if len(output) >= 2000:
            await utils.delay_send(msg.channel, client.messages["ms_too_large"])
        else:
            await utils.delay_send(msg.channel, output)
