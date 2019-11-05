from . import Command
from .. import utils
import discord
import requests
import re


class Uptime(Command):
    names = ["status", "ping", "uptime"]
    description = "Checks if a website is down"
    needsContent = False

    async def execute_command(self, client, msg, content):
        if content:
            urls = content.split()
        else:
            urls = client.config["default_uptime_urls"]

        msg_to_send = ""
        for url in urls:
            status_code = -1

            # Adds a .com to end of urls that dont have a tld
            # this just assumes you mean .com but if the websit should be say
            # .edu it wont work
            if not re.search(r".\..", url):
                url = url + ".com"

            try:
                try:
                    r = requests.head(url, allow_redirects=True)
                    status_code = r.status_code
                except requests.exceptions.MissingSchema:
                    url = f"https://{url}"
                    r = requests.head(url, allow_redirects=True)
                    status_code = r.status_code
            except:
                status_code = -1
                pass

            if validStatusCode(status_code):
                msg_to_send += f"<{url}> is up\n"
            else:
                msg_to_send += f"<{url}> is down. Status code: {status_code}\n"
        embed = discord.Embed(
            title="Relevant Website Statuses", description=msg_to_send
        )
        await msg.channel.send(embed=embed)


def validStatusCode(sc):
    if sc == 200:
        return True
    elif sc == 401:
        return True

    return False
