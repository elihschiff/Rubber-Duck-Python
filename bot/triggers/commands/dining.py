from . import Command
from .. import utils
import urllib
from bs4 import BeautifulSoup
import requests
import discord
import datetime
import calendar


class Dining(Command):
    names = ["dining"]
    description = "Gets currently available dining halls on campus"
    usage = f"{prefixes[0]}dining"

    async def execute_command(self, client, msg, content):
        DINING_HALL_LENGTH = 45
        try:
            day = calendar.day_name[datetime.datetime.now().weekday()]
            time = datetime.datetime.now().time()
            minute = time.hour * 60 + time.minute
            page_link = "https://rensselaerdining.com/dining-near-me/open-now"
            page_response = requests.get(page_link, timeout=30)
            page_content = page_content = BeautifulSoup(
                page_response.content, "html.parser"
            )
            locs = page_content.findAll("div", {"class": "dining-halls-container"})
            message = ""
            embed = discord.Embed(
                title="Currently available dining halls",
                description=message,
                color=0x00FF00,
            )
            for s in locs:
                link = None
                btn_group = s.find("div", {"class": "button-group"})
                if btn_group != None:
                    if btn_group.find("a") != None:
                        link = btn_group.find("a")["href"]

                hours = s.findAll("div", {"class": "operation-hours-block"})
                for h in hours:
                    if day in h["data-regdays"]:
                        if minute >= int(h["data-reghoursstart"]) and minute <= int(
                            h["data-reghoursend"]
                        ):
                            hoursStart = str(int(h["data-reghoursstart"]) // 60)
                            minutesStart = str(int(h["data-reghoursstart"]) % 60).zfill(
                                2
                            )
                            hoursEnd = str(int(h["data-reghoursend"]) // 60)
                            minutesEnd = str(int(h["data-reghoursend"]) % 60).zfill(2)
                            dining_hall = s.find(
                                "div", {"class": "dining-halls-block-left"}
                            ).text
                            dining_hall = dining_hall.strip()
                            time = (
                                f"{hoursStart}:{minutesStart} - {hoursEnd}:{minutesEnd}"
                            )

                            if link != None:
                                if link[:2] == "//":
                                    link = "https:" + link
                                embed.add_field(
                                    name=f"{dining_hall} -- {time}",
                                    value=f"[Menu]({link})",
                                    inline=False,
                                )
                            break

            await utils.delay_send(msg.channel, "", 0, embed=embed)
        except:
            await utils.delay_send(
                msg.channel, "An error occurred in finding dining halls"
            )
            await utils.sendTraceback(client, msg.content)
