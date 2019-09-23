from bs4 import BeautifulSoup

from . import Command
from .. import utils
import requests
import re


class Java(Command):
    names = ["java"]
    description = "Sends a link to a Java reference page if it exists (JavaSE 13)"
    needsContent = True

    async def execute_command(self, client, msg, content):
        if len(content) > 0:
            r = requests.get(
                f"https://docs.oracle.com/apps/search/search.jsp?q={content}&category=java&product=en"
                f"/java/javase/13"
            )
            soup = BeautifulSoup(r.text, "html.parser")
            result = f'Potential matches for "{content}":\n'
            for text in soup.find_all("div", attrs={"class": "srch-result"}):
                if (
                    "Java Platform, Standard Edition Java API Reference, Java SE 13"
                    in text.contents[1].getText()
                ):
                    if (
                        len(text.contents) > 3
                        and content.lower() in text.contents[3].getText().lower()
                        and len(text.contents[3].contents) > 0
                    ):
                        if (
                            "class-use" not in text.contents[3].contents[0]["href"]
                            and "api" in text.contents[3].contents[0]["href"]
                        ):
                            result += text.contents[3].contents[0]["href"] + "\n"
            if result == f'Potential matches for "{content}":\n':
                await utils.delay_send(
                    msg.channel, f'Could not find Javadoc page for "{content}"'
                )
                return
            await utils.delay_send(msg.channel, result)
