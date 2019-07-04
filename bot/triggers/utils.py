import time
import asyncio


async def delay_send(channel, msg, delay_factor=1.0):
    delay = 1 + 0.05 * len(msg) * delay_factor

    async with channel.typing():
        await asyncio.sleep(delay)

    await channel.send(msg)
