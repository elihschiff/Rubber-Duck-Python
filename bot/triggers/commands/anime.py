from . import Command
from .. import utils
from jikanpy import Jikan
import nextcord


class Anime(Command):
    names = ["anime"]
    description = "Sends a description of an anime using MAL."
    usage = "!anime [Name of anime]"
    examples = "!anime hunter x hunter"

    async def execute_command(self, client, msg, content, **kwargs):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}", reply_to=msg)
            return

        jikan = Jikan()
        show = jikan.search("anime", content)["results"][0]

        if show["rated"] == "Rx" or show["rated"] == "R+":
            await utils.delay_send(
                msg.channel, "Sorry, I can't give info on NSFW shows.", reply_to=msg
            )
            if msg.channel.type is not nextcord.ChannelType.private:
                await msg.delete()
            return

        embed = nextcord.Embed(
            title=show["title"], url=show["url"], description=show["synopsis"]
        )
        embed.set_image(url=show["image_url"])

        await utils.delay_send(msg.channel, "", embed=embed, reply_to=msg)
