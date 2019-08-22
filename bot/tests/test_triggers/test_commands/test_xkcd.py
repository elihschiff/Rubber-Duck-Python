import unittest
import json
import requests
import re
import urllib
from PIL import Image, ImageOps
import os
import math
from functools import reduce
import operator

from ... import test_utils
from ....duck import DuckClient


class TestXkcd(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_xkcd(self):
        test_strings = [
            [
                "standards",
                "https://imgs.xkcd.com/comics/standards.png",
                "**Standards:** Fortunately, the charging one has been solved now that we've all standardized on mini-USB. Or is it micro-USB? Shit.",
            ],
            [
                "xkcd phone 2",
                "https://imgs.xkcd.com/comics/xkcd_phone_2.png",
                "**xkcd Phone 2:** Washable, though only once.",
            ],
        ]
        for string in test_strings:
            msg = test_utils.init_message(f"!xkcd {string[0]}")
            await self.client.on_message(msg)
            tmpLocation = f"/tmp/{string[0]}"
            urllib.request.urlretrieve(string[1], tmpLocation)

            expected_img = Image.open(tmpLocation)
            self.assertIsNotNone(msg.channel.filename)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertEqual(msg.channel.test_result, string[2])
            h1 = expected_img.histogram()
            h2 = Image.open(msg.channel.filename).histogram()

            self.assertEqual(len(h1), len(h2))

            rms = math.sqrt(
                reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2)) / len(h1)
            )

            self.assertTrue(rms < 150)
            os.remove(msg.channel.filename)

    @test_utils.async_test
    async def test_xkcd_empty(self):
        for num_spaces in range(0, 1):
            msg = test_utils.init_message("!xkcd" + " " * num_spaces)
            await self.client.on_message(msg)
            self.assertIsNotNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNotNone(msg.channel.filename)

    @test_utils.async_test
    async def test_xkcd_from_bot(self):
        test_strings = ["java", "python"]
        for string in test_strings:
            msg = test_utils.init_message(f"!tex {string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)
