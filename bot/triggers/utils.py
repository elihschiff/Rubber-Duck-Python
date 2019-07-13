import time
import asyncio


async def delay_send(channel, msg, delay_factor=1.0, embed=None):
    delay = 0.5 + 0.003 * len(msg) * delay_factor
    # print(delay)
    delay = max(2, delay)

    async with channel.typing():
        await asyncio.sleep(delay)

    await channel.send(msg, embed=embed)
