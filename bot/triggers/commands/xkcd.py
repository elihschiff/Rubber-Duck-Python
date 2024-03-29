from . import Command
from .. import utils
import nextcord
import xkcd
from nextcord import Embed


class Xkcd(Command):
    names = ["xkcd"]
    description = "Finds a relevant xkcd using a keyword or comic number"
    usage = "!xkcd [(optional) search term]"
    examples = "!xkcd, !xkcd duck, !xkcd 537"
    show_in_help = True

    def get_comic(self, number):
        if number == None:
            comic = xkcd.getRandomComic()
        else:
            comic = xkcd.getComic(number)

        embed = Embed(description=comic.getAltText())
        embed.set_author(name=comic.getTitle())
        embed.set_image(url=comic.getImageLink())
        return embed

    async def execute_command(self, client, msg, content, **kwargs):
        if len(content) == 0:
            embed = self.get_comic(None)
        else:
            if content.isnumeric():
                num = int(content)
            else:
                async with utils.get_aiohttp().get(
                    f"https://relevant-xkcd.com/={content}",
                ) as req:
                    data = await req.text()

                if req.status == 200:
                    xkcd_str = 'href="https://www.xkcd.com/'
                    data = data[data.find(xkcd_str) :]
                    num = int(data[len(xkcd_str) : data.find('">')])

            try:
                # Don't make additional requests on 404 (or invalid)
                if num == None or num == 404:
                    raise ValueError()
                embed = self.get_comic(num)
            except:
                return await utils.delay_send(
                    msg.channel,
                    client.messages["no_xkcd_found"].format(content),
                    reply_to=msg,
                )
        await msg.channel.send(
            embed=embed,
            reference=msg,
            mention_author=True,
        )
