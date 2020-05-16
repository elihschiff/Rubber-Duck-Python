import random

import discord

from . import utils
from ..duck import DuckClient


def should_quack(client: DuckClient, msg: discord.Message) -> bool:
    if client.user.mentioned_in(msg):
        return True

    if msg.channel.type is discord.ChannelType.private:
        return True

    return msg.channel.id in client.config["quack_channels"]


async def quack(client: DuckClient, msg: discord.Message) -> None:
    if should_quack(client, msg):
        quack_msg = random.choice(client.quacks)
        await utils.delay_send(msg.channel, quack_msg)
