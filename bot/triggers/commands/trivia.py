from . import Command
from .. import utils
from json import dumps
import nextcord
import html


class Trivia(Command):
    names = ["trivia"]
    description = "Loads a trivia question"
    usage = "!trivia"
    examples = "!trivia"
    causes_spam = True

    async def execute_command(self, client, msg, content, **kwargs):

        page_link = "https://opentdb.com/api.php?amount=1"

        for i in range(2):
            async with utils.get_aiohttp().get(page_link) as page_response:
                response = await page_response.json()

            if response["response_code"] != 0:
                try:
                    message = [
                        "Error loading trivia question: No Results",
                        "Error loading trivia question: Invalid Parameters",
                        "Error loading trivia question: Token Not Found",
                        "Error loading trivia question: Token Empty",
                    ][response.response_code - 1]

                except IndexError:
                    message = "Error loading trivia question: Unknown Response Code"

                await utils.delay_send(msg.channel, msg=message, reply_to=msg)
                return

            category = html.unescape(response["results"][0]["category"])
            difficulty = html.unescape(response["results"][0]["difficulty"])
            question = html.unescape(response["results"][0]["question"])
            answers = [
                (html.unescape(response["results"][0]["correct_answer"]), True)
            ] + [
                (html.unescape(answer), False)
                for answer in response["results"][0]["incorrect_answers"]
            ]

            if response["results"][0]["type"] == "boolean":
                answers = sorted(answers, key=lambda x: x[0])[::-1]
            else:
                answers = sorted(answers, key=lambda x: x[0])

            formated_answers = "\n".join(
                ("||:white_check_mark:||  " if a[1] else "||:x:||  ") + a[0]
                for a in answers
            )
            trivia = f"{question}\n\n {formated_answers}"
            if len(trivia) <= 2000:
                response = nextcord.Embed(
                    title=category,
                    description=trivia,
                    colour={
                        "easy": nextcord.Color.dark_blue(),
                        "medium": nextcord.Color.orange(),
                        "hard": nextcord.Color.red(),
                    }[difficulty],
                )
                await utils.delay_send(msg.channel, embed=response, reply_to=msg)
                return

        await utils.delay_send(
            msg.channel, "Error loading trivia question: Please Try Again", reply_to=msg
        )
