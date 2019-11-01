from . import Command
from .. import utils
import discord
import requests
import urllib.request
import os
import json


class Uptime(Command):
    names = ["status", "ping", "uptime"]
    description = "Checks if a website is down"
    needsContent = False

    async def execute_command(self, client, msg, content):
        if(content):
            status_code = 0
            try:
                try:
                    r = requests.head(content, allow_redirects=True)
                    status_code = r.status_code
                except requests.exceptions.MissingSchema:
                    content = f"https://{content}"
                    r = requests.head(content, allow_redirects=True)
                    status_code = r.status_code
            except:
                pass

            if validStatusCode(status_code):
                await utils.delay_send(
                            msg.channel, "<{}> is up".format(content)
                        )
                return
            else:
                await utils.delay_send(
                            msg.channel, "<{}> is down. Status code: {}".format(content,status_code)
                        )
                return
        else:
            #no content deafult to config file

            try:
                msg_to_send = ""
                for url in client.config["default_uptime_urls"]:
                    r = requests.head(url, allow_redirects=True)
                    status_code = r.status_code
                    if validStatusCode(status_code):
                        msg_to_send += f"<{url}> is up\n"
                    else:
                        msg_to_send += f"<{url}> is down. Status code: {status_code}\n"

                embed=discord.Embed(title="Relevant Website Statuses", description=msg_to_send)
                await msg.channel.send(embed=embed)

            except:
                await utils.sendTraceback(self, "This may mean an invalid url in your config file")


def validStatusCode(sc):
    if(sc == 200):
        return True;
    elif(sc == 401):
        return True;

    return False
