from . import Command
from .. import utils
from sympy import *
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
)

transformations = standard_transformations + (implicit_multiplication_application,)


class Cancel(Command):
    names = ["cancel"]
    description = (
        "Take any rational function and put it into the standard canonical form, p and q, "
        "where p and q are expanded polynomials with no common factors, and the "
        "leading coefficients of p and q do not have denominators (i.e., are integers)."
    )
    usage = "!Cancel"

    async def execute_command(self, client, msg, content):
        try:
            output = str(
                cancel(parse_expr(content, transformations=transformations))
            ).replace("*", "\*")
            await utils.delay_send(msg.channel, output, 0)
        except:
            await utils.delay_send(msg.channel, "Invalid Expression :(", 0)
