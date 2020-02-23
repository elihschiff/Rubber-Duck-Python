from bs4 import BeautifulSoup

from . import Command
from .. import utils
import requests
import re
import os.path
import time
import urllib.request
import ast


class Java(Command):
    names = ["java"]
    description = "Sends a link to a Java reference page if it exists (JavaSE 13)"
    usage = f"{prefixes[0]}java [module/package/tag/type/member]"
    examples = f"{prefixes[0]}java clear, {prefixes[0]}java java.base"

    def get_file_age(self, filepath):
        return time.time() - os.path.getmtime(filepath)

    def search_dict(self, search, file):
        if not os.path.exists(file[0]) or self.get_file_age(file[0]) > 2678400:
            urllib.request.urlretrieve(file[1], file[0])
        if os.path.exists(file[0]):
            with open(file[0], "r") as readFile:
                data = readFile.read()
                match = re.search(
                    re.escape(f'"l":"{search}"'), data, flags=re.IGNORECASE
                )
                if match:
                    left_index = match.start()
                    while left_index >= 0 and data[left_index] != "{":
                        left_index -= 1
                    data_size = len(data)
                    right_index = match.start()
                    while right_index < data_size - 1 and data[right_index] != "}":
                        right_index += 1
                    right_index += 1
                    if right_index != data_size and left_index != -1:
                        return ast.literal_eval(data[left_index:right_index])
        return None

    def search_index(self, search):
        save_location = "/tmp/"
        baseapi = "http://docs.oracle.com/en/java/javase/13/docs/api/"
        # other java search only returns html; the java api autoredirects to https
        files = [
            [
                os.path.join(save_location, "java_module-search-index.js"),
                "https://docs.oracle.com/en/java/javase/13/docs/api/module-search-index.js",
            ],
            [
                os.path.join(save_location, "java_package-search-index.js"),
                "https://docs.oracle.com/en/java/javase/13/docs/api/package-search-index.js",
            ],
            [
                os.path.join(save_location, "java_tag-search-index.js"),
                "https://docs.oracle.com/en/java/javase/13/docs/api/tag-search-index.js",
            ],
            [
                os.path.join(save_location, "java_type-search-index.js"),
                "https://docs.oracle.com/en/java/javase/13/docs/api/type-search-index.js",
            ],
            [
                os.path.join(save_location, "java_member-search-index-js"),
                "https://docs.oracle.com/en/java/javase/13/docs/api/member-search-index.js",
            ],
        ]
        dictionary = self.search_dict(search, files[0])
        if dictionary:
            return baseapi + dictionary["l"] + "/module-summary.html"
        dictionary = self.search_dict(search, files[1])
        if dictionary:
            return (
                baseapi
                + dictionary["m"]
                + "/"
                + dictionary["l"].replace(".", "/")
                + "/package-summary.html"
            )
        dictionary = self.search_dict(search, files[2])
        if dictionary:
            return baseapi + dictionary["u"]
        dictionary = self.search_dict(search, files[3])
        if dictionary:
            return (
                baseapi
                + self.search_dict(dictionary["p"], files[1])["m"]
                + "/"
                + dictionary["p"].replace(".", "/")
                + "/"
                + dictionary["l"]
                + ".html"
            )
        if "." in search:
            dictionary = self.search_dict(search.rsplit(".", 1)[-1], files[3])
            if dictionary:
                return (
                    baseapi
                    + self.search_dict(dictionary["p"], files[1])["m"]
                    + "/"
                    + dictionary["p"].replace(".", "/")
                    + "/"
                    + dictionary["l"]
                    + ".html"
                )
        dictionary = self.search_dict(search, files[4])
        if dictionary:
            if "url" in dictionary:
                return (
                    baseapi
                    + self.search_dict(dictionary["p"], files[1])["m"]
                    + "/"
                    + dictionary["p"].replace(".", "/")
                    + "/"
                    + dictionary["c"]
                    + ".html"
                    + "#"
                    + dictionary["url"]
                )
            else:
                return (
                    baseapi
                    + self.search_dict(dictionary["p"], files[1])["m"]
                    + "/"
                    + dictionary["p"].replace(".", "/")
                    + "/"
                    + dictionary["c"]
                    + ".html"
                    + "#"
                    + dictionary["l"]
                )

    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {usage}")
            return

        r = requests.get(
            f"https://docs.oracle.com/apps/search/search.jsp?q={content}&category=java&product=en"
            f"/java/javase/13"
        )
        search = self.search_index(content)
        soup = BeautifulSoup(r.text, "html.parser")
        result = f"Potential match(es) for `{content}`:\n"
        if search:
            result += search + "\n"
        else:
            search = ""
        for text in soup.find_all("div", attrs={"class": "srch-result"}):
            if (
                "Java Platform, Standard Edition Java API Reference, Java SE 13"
                in text.contents[1].getText()
            ):
                if (
                    len(text.contents) > 3
                    and content.lower() in text.contents[3].getText().lower()
                    and len(text.contents[3].contents) > 0
                ):
                    if (
                        "class-use" not in text.contents[3].contents[0]["href"]
                        and "api" in text.contents[3].contents[0]["href"]
                        and text.contents[3].contents[0]["href"] != search
                    ):
                        result += text.contents[3].contents[0]["href"] + "\n"
        if result == f"Potential match(es) for `{content}`:\n":
            await utils.delay_send(
                msg.channel, f"Could not find Javadoc page for `{content}`"
            )
            return
        await utils.delay_send(msg.channel, result)
