from . import Command
from .. import utils
import wolframalpha


class Math(Command):
    names = ["math", "calc", "calculate", "solve"]
    description = "Solves a math problem"
    description2 = """**Description:** Solves a math problem
                      **Usage:** !math [expression]
                      **Examples:** !math d/dx sin(x)^2, !math 219 to binary
                      **Alternate names:** !calc, !calculate"""
    needsContent = True

    async def execute_command(self, client, msg, content):
        wolfram = wolframalpha.Client(client.config["WOLFRAM_ID"])
        query_res = wolfram.query(content)
        try:
          for pod in query_res.pods:
              if (
                  pod.title.startswith("Result")
                  or pod.title.startswith("Exact result")
                  or pod.title.startswith("Power of 10 representation")
                  or pod.title.startswith("Decimal approximation")
              ):
                  await msg.channel.send(f"The answer for `{content}` is: `{pod.text}`")
                  return

              if pod.title.startswith("Plot"):
                  await msg.channel.send(
                      # TODO: this should be more robust
                      f"The answer for `{content}` is: {list(list(pod.subpod)[0].img)[0]['@src']}"
                  )
                  return
        except KeyError:
          pass
        await msg.channel.send(f"I could not find an answer for `{content}`")
