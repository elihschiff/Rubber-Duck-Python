from . import Command
from .. import utils
from sympy import *
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

transformations=(standard_transformations + (implicit_multiplication_application,))

class ExpandFunc(Command):
    names = ["expandfunc"]
    description = "Simplifies an expression"
    usage = "!expandfunc"

    async def execute_command(self, client, msg, content):
        output = str(expand_func(parse_expr(content, transformations=transformations))).replace('*', '\*')
        await utils.delay_send(msg.channel, output, 0)
