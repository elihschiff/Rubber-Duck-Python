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


class TestLatex(unittest.TestCase):
    def setUp(self):
        self.client = DuckClient()
        self.client._connection.user = test_utils.MockUser()

    @test_utils.async_test
    async def test_latex(self):
        return
        test_strings = ["$quack$", "\\Sigma"]
        for string in test_strings:
            msg = test_utils.init_message(f"!tex {string}")
            await self.client.on_message(msg)

            data = json.dumps(
                {
                    "auth": {"user": "guest", "password": "guest"},
                    "latex": string,
                    "resolution": 600,
                    "color": "FFFFFF",
                }
            )

            response = requests.post(
                "http://latex2png.com/api/convert", data=data, verify=False
            )
            json_response = json.loads(response.text)

            if "url" in json_response:
                sub_url = json_response["url"]
                url = f"http://latex2png.com{sub_url}"
                image_id = sub_url.split("/")[2]
                tmpLocation = f"/tmp/{image_id}"
                urllib.request.urlretrieve(url, tmpLocation)

                expected_img = Image.open(tmpLocation)
                borderSizeX, borderSizeY = expected_img.size
                borderSizeX = math.ceil(borderSizeX / 20)
                borderSizeY = 0
                expected_img_with_border = ImageOps.expand(
                    expected_img,
                    border=(borderSizeX, borderSizeY, borderSizeX, borderSizeY),
                    fill="#00000000",
                )

                self.assertIsNotNone(msg.channel.filename)
                self.assertIsNone(msg.channel.embed_dict)
                self.assertEqual(msg.channel.test_result, "")
                h1 = expected_img.histogram()
                h2 = Image.open(msg.channel.filename).histogram()

                self.assertEqual(len(h1), len(h2))

                rms = math.sqrt(
                    reduce(operator.add, map(lambda a, b: (a - b) ** 2, h1, h2))
                    / len(h1)
                )

                self.assertTrue(rms < 150)

                os.remove(msg.channel.filename)

    @test_utils.async_test
    async def test_latex_empty(self):
        for num_spaces in range(0, 1):
            msg = test_utils.init_message("!tex" + " " * num_spaces)
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)

    @test_utils.async_test
    async def test_latex_from_bot(self):
        test_strings = ["$quack$", "\\Sigma"]
        for string in test_strings:
            msg = test_utils.init_message(f"!tex {string}")
            msg.author.bot = True
            await self.client.on_message(msg)
            self.assertIsNone(msg.channel.test_result)
            self.assertIsNone(msg.channel.embed_dict)
            self.assertIsNone(msg.channel.filename)
