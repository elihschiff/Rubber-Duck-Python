import asyncio


async def delay_send(sendable, msg, delay_factor=1.0, embed=None):
    delay = (0.5 + 0.003 * len(msg)) * delay_factor

    delay = min(2, delay)
    delay = max(0.25, delay)

    await asyncio.sleep(delay)

    return await sendable.send(msg, embed=embed)


def sanitize(msg):
    return msg.replace("`", "''")
