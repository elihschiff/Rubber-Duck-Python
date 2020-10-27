from . import Command
from .. import utils
from jikanpy import Jikan
import discord


class Anime(Command):
    names = ["anime"]
    description = "Sends a description of an anime using MAL."
    usage = "!anime [Name of anime]"
    examples = f"!anime hunter x hunter"

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        jikan = Jikan()
        show = jikan.search("anime", content)["results"][0]

        if show["rated"] == "Rx" or show["rated"] == "R+":
            await utils.delay_send(
                msg.channel, "Sorry, I can't give info on NSFW shows."
            )
            if msg.channel.type is not discord.ChannelType.private:
                await msg.delete()
            return

        embed = discord.Embed(
            title=show["title"], url=show["url"], description=show["synopsis"]
        )
        embed.set_image(url=show["image_url"])

        await utils.delay_send(msg.channel, "", embed=embed)
