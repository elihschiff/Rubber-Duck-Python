from . import Command
from .. import utils
from sympy import *
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
)

transformations = standard_transformations + (implicit_multiplication_application,)


class CombSimp(Command):
    names = ["combsimp"]
    description = "Simplifies combinatorial expressions"
    usage = "!combsimp"

    async def execute_command(self, client, msg, content):
        try:
            output = str(
                combsimp(parse_expr(content, transformations=transformations))
            ).replace("*", "\*")
            await utils.delay_send(msg.channel, output, 0)
        except:
            await utils.delay_send(msg.channel, "Invalid Expression :(", 0)
