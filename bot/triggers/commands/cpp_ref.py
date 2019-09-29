from . import Command
from .. import utils
import requests


# next task: what if len args > 2?? HERE***


class CppRef(Command):
    names = ["cpp"]
    description = "Sends a link to a cpp reference page, if it exists"
    needsContent = True

    async def execute_command(self, client, msg, content):
        args = content.split(" ")

        # check if first link works
        if len(args) >= 1:
            # creating url from content after !cpp assuming it's a stl container
            first = args[0]
            url = f"http://www.cplusplus.com/reference/stl/{first}/"
            r = requests.get(url)
            if "<h1>404 Page Not Found</h1>" in r.text:
                # stl container attempt didn't work
                # try to see if it's an iostream class or object
                # which has multiple possible links, not just "stl" like with
                # stl containers, so try with all links, listed in try_list
                try_list = [
                    "iostream",
                    "ios",
                    "fstream",
                    "ostream",
                    "istream",
                    "iomanip",
                ]
                for i in range(0, len(try_list) - 1):
                    url = f"http://www.cplusplus.com/reference/{try_list[i]}/{first}/"
                    r = requests.get(url)
                    if "<h1>404 Page Not Found</h1>" not in r.text:
                        break
                if "<h1>404 Page Not Found</h1>" in r.text:
                    # last attempt: maybe it is its own link not under a thread
                    url = f"http://www.cplusplus.com/reference/{first}/{first}/"
                    r = requests.get(url)
                    if "<h1>404 Page Not Found</h1>" in r.text:
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
        if len(args) >= 3:
            # Too many arguments. Still checking for url from first two args but
            # notifying user their other arguments won't be used.
            await utils.delay_send(
                msg.channel,
                f"Too many arguments. Use format: \
!cpp [container/class/object] [(optional) member function]",
            )
        if len(args) >= 2:
            # get the second part of the url if the user entered an optional
            # member function
            second = args[1]
            url2 = url + f"{second}/"
            r2 = requests.get(url2)
            if "<h1>404 Page Not Found</h1>" in r2.text:
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
