from . import utils
import random

from nextcord import ChannelType


def should_quack(client, msg) -> bool:
    if client.user.mentioned_in(msg):
        return True

    if msg.channel.type is ChannelType.private:
        return True

    return msg.channel.id in client.config["quack_channels"]


async def quack(client, msg):
    if should_quack(client, msg):
        quack = random.choice(client.quacks)
        await utils.delay_send(msg.channel, quack)
