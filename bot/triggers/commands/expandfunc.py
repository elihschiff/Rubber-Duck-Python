from . import Command
from .. import utils
from sympy import *
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
)

transformations = standard_transformations + (implicit_multiplication_application,)


class ExpandFunc(Command):
    names = ["expandfunc"]
    description = "Expands special functions in terms of some identities."
    usage = "!expandfunc"

    async def execute_command(self, client, msg, content):
        try:
            output = str(
                expand_func(parse_expr(content, transformations=transformations))
            ).replace("*", "\*")
            await utils.delay_send(msg.channel, output, 0)
        except:
            await utils.delay_send(msg.channel, "Invalid Expression :(", 0)
