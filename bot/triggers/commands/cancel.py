from . import Command
from .. import utils
from sympy import *
from sympy.parsing.sympy_parser import standard_transformations, implicit_multiplication_application

transformations=(standard_transformations + (implicit_multiplication_application,))

class Cancel(Command):
    names = ["cancel"]
    description = "Simplifies an expression"
    usage = "!Cancel"

    async def execute_command(self, client, msg, content):
        output = str(cancel(parse_expr(content, transformations=transformations))).replace('*', '\*')
        await utils.delay_send(msg.channel,output, 0)
