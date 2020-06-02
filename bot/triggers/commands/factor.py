from . import Command
from .. import utils
from sympy import *
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
)

transformations = standard_transformations + (implicit_multiplication_application,)


class Factor(Command):
    names = ["factor"]
    description = "Takes a polynomial and factors it into irreducible factors over the rational numbers."
    usage = "!factor"

    async def factor(self, client, msg, content):
        try:
            output = str(
                factor(parse_expr(content, transformations=transformations))
            ).replace("*", "\*")
            await utils.delay_send(msg.channel, output, 0)
        except:
            await utils.delay_send(msg.channel, "Invalid Expression :(", 0)
