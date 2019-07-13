from . import Command
from .. import utils
import discord
import requests
import json


class Minecraft(Command):
    names = ["minecraft", "mc"]
    description = "Get the minecraft server ip and view current server status"
    needsContent = False

    async def execute_command(self, client, msg, content):
        data = requests.get(
            url="https://mcapi.us/server/status",
            params={"ip": client.config["minecraft"]["ip"]},
        ).json()
        description = (
            "**IP: ** "
            + client.config["minecraft"]["ip"]
            + "\n**Status: ** "
            + data["status"]
            + "\n**Players: ** "
            + str(data["players"]["now"])
            + "/"
            + str(data["players"]["max"])
        )
        embed = discord.Embed(description=description, color=0x3E5C20)
        embed.set_author(
            name="⁠", icon_url="https://discordemoji.com/assets/emoji/grassblock.png"
        )
        embed.set_footer(
            text="Minecraft server is courtesy of @"
            + msg.channel.guild.get_member(
                int(client.config["minecraft"]["host_id"])
            ).display_name
        )
        await msg.channel.send(embed=embed)
