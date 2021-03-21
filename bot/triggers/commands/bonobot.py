from . import Command
from .. import utils


class Bonobot(Command):
    names = ["bonobot"]
    description = "Sends a bonobo"
    usage = "!bonobot [ping users here]"
    example = "!bonobot @Phi11ipus @Eigenvector"
    causes_spam = True

    async def execute_command(self, client, msg, content, **kwargs):
        return
