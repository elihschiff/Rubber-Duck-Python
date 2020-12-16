from . import Command
from .. import utils
import wolframalpha


class Math(Command):
    names = ["math", "calc", "calculate", "solve"]
    description = "Solves a math problem"
    usage = "!math [expression]"
    examples = f"!math d/dx sin(x)^2"

    async def execute_command(self, client, msg, content, **kwargs):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        wolfram = wolframalpha.Client(client.config["wolfram_id"])
        res = wolfram.query(content)
        try:
            result = next(res.results)

            if result.title.startswith("Plot"):
                await msg.channel.send(
                    f"The answer for `{content}` is: {result.subpod.img['@src']}"
                )
            else:
                await msg.channel.send(
                    f"The answer for `{content}` is: `{result.plainText}`"
                )
        except StopIteration:
            pass
        await msg.channel.send(
            f"I could not find an answer for `{utils.sanitized(content)}`"
        )
