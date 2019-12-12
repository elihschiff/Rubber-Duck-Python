import asyncio
from contextlib import contextmanager
import random


async def delay_send(sendable, msg, delay_factor=1.0, embed=None):
    delay = (0.5 + 0.003 * len(msg)) * delay_factor

    delay = min(2, delay)
    delay = max(0.25, delay)

    await asyncio.sleep(delay)

    return await sendable.send(msg, embed=embed)


def sanitize(msg):
    return msg.replace("`", "''")


@contextmanager
async def remote_file(aiohttp, url, filename=None):
    if filname.startswith("/tmp/"):
        filename = filename[5:]

    if not filename:
        filename = random.random()

    response = await aiohttp.get(url)
    file_content = await response.read()

    with open(f"/tmp/{filename}", "wb") as f:
        f.write(file_content)

    try:
        with open(f"/tmp/{filename}", "rb") as f:
            yield f
    finally:
        os.remove(f"/tmp/{filename}")
