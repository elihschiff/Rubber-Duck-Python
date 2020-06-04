from . import Command
from .. import utils
from sympy import *
from sympy.parsing.sympy_parser import (
    standard_transformations,
    implicit_multiplication_application,
)

transformations = standard_transformations + (implicit_multiplication_application,)


class Apart(Command):
    names = ["apart"]
    description = "Performs a partial fraction decomposition on a rational function."
    usage = "!apart"
    causes_spam = True

    async def execute_command(self, client, msg, content):
        try:
            output = str(
                apart(parse_expr(content, transformations=transformations))
            ).replace("*", "\*")
            await utils.delay_send(msg.channel, output, 0)
        except:
            await utils.delay_send(msg.channel, "Invalid Expression :(", 0)
