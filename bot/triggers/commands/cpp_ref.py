from bs4 import BeautifulSoup
import requests

from . import Command
from .. import utils


class CppRef(Command):
    names = ["cpp"]
    description = "Sends a link to a cpp reference page, if it exists"
    usage = "!usage [container/class/object] [(optional) member function]"
    examples = f"!usage vector push_back, !cpp sort"

    async def execute_command(self, client, msg, content):
        args = content.split(" ")

        if not content:
            await utils.delay_send(msg.channel, "Usage: " + usage)
            return

        # check if link using just the first arg works
        if len(args) >= 1:
            first = args[0]
            # getting all sub_links from the main page
            main_page = f"http://www.cplusplus.com/reference/"
            page_content = requests.get(main_page)
            soup = BeautifulSoup(page_content.text, "html.parser")
            links = soup.find_all("a")
            # keep trying different sublinks until either something works
            # and we break out of the loop, or loop ends
            for link in links:
                sub_link = str(link["href"])
                # only want links for reference pages (not contact, info, etc.
                # links that accidentally work)
                if sub_link[0:10] != "/reference":
                    continue
                url = f"http://www.cplusplus.com{sub_link}{first}/"
                page_content = requests.get(url)
                if "<h1>404 Page Not Found</h1>" not in page_content.text:
                    break
            if "<h1>404 Page Not Found</h1>" in page_content.text:
                # last attempt: maybe it is its own link not under a thread
                url = f"http://www.cplusplus.com/reference/{first}/{first}/"
                page_content = requests.get(url)
                if "<h1>404 Page Not Found</h1>" in page_content.text:
                    # no links work
                    # return an error to the user in discord and exit function
                    await utils.delay_send(
                        msg.channel,
                        f"Could not find cpp page for `{content}`.\
\nUse format: !cpp [container/class/object] [(optional) member function]",
                    )
                    return

        # This code only runs if there is a valid url formed from previous
        # if statement (otherwise we retured). Check if specifying second
        # argument works.
        if len(args) == 1:
            # only one argument, so return url found
            await utils.delay_send(msg.channel, url)
        elif len(args) >= 3:
            # Too many arguments. Still checking for url from first two args but
            # notifying user their other arguments won't be used.
            await utils.delay_send(
                msg.channel,
                f"Too many arguments. Use format: \
!cpp [container/class/object] [(optional) member function]",
            )
        elif len(args) >= 2:
            # get the second part of the url if the user entered an optional
            # member function
            second = args[1]
            url2 = url + f"{second}/"
            page_content = requests.get(url2)
            if "<h1>404 Page Not Found</h1>" in page_content.text:
                # second argument doesn't work but first one does
                # inform user in discord, send first link, and exit function
                await utils.delay_send(
                    msg.channel,
                    f"Could not find cpp page for {content} with {second}\
, but found the general page with {first}.",
                )
                await utils.delay_send(msg.channel, url)
                return
            else:
                # only other condition: both second and first argument work
                # send link to user and exit function
                await utils.delay_send(msg.channel, url2)
                return
