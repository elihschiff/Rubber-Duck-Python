import time
import asyncio
import nextcord
import re
import traceback
import aiohttp


async def delay_send(
    sendable, msg="", delay_factor=0.5, embed=None, file=None, files=None, reply_to=None
):
    async with sendable.typing():
        delay = (0.5 + 0.003 * len(msg)) * delay_factor

        # delay will never take more than 1 seconds to respond
        delay = min(1, delay)
        # delay will never take less than .125 seconds to respond
        delay = max(0.125, delay)
        # delay = 0
        # async with sendable.typing():
        await asyncio.sleep(delay)

        return await sendable.send(
            msg,
            embed=embed,
            file=file,
            files=files,
            reference=reply_to,
            mention_author=True,
        )


emoji_numbers = [
    "\u0030\u20E3",
    "\u0031\u20E3",
    "\u0032\u20E3",
    "\u0033\u20E3",
    "\u0034\u20E3",
    "\u0035\u20E3",
    "\u0036\u20E3",
    "\u0037\u20E3",
    "\u0038\u20E3",
    "\u0039\u20E3",
]

no_matching_results_emote = "🚫"


async def generate_react_menu(
    sendable, user_id, opening_message, max_length, option_list, cancel_message
):
    max_length = min(max_length, len(emoji_numbers))

    msg_to_send = f"<@{user_id}>"
    msg_to_send += opening_message
    for i in range(min(max_length, len(option_list))):
        msg_to_send += f"\n\n{emoji_numbers[i]} {option_list[i]}"
    msg_to_send += f"\n\n{no_matching_results_emote} {cancel_message}"
    sent_msg = await sendable.send(msg_to_send)
    for i in range(min(max_length, len(option_list))):
        await sent_msg.add_reaction(emoji_numbers[i])
    await sent_msg.add_reaction(no_matching_results_emote)


def user_is_mod(client, user) -> bool:
    if user.id in (752702081915420783, 141900800095027201, 226503278760820746):
        return True

    if not hasattr(user, "roles"):
        user = client.SERVER.get_member(user.id)

    for role in user.roles:
        if role.id == client.config["mod_role_id"]:
            return True

    return False


def user_in_timeout(client, user) -> bool:
    member = client.SERVER.get_member(user.id)
    if member is None:
        return False

    for role in member.roles:
        if role.id == client.config["time_out_id"]:
            return True

    return False


def has_flag(flag, content):
    """Determines if a command's content contains a flag.

    Arguments:
    flag -- the flag for which to search
    content -- the content of the command
    """
    return "-" + flag in content.split()


def get_flag(flag, content, default=None):
    """Finds the value associated with a flag in a command's content.

    Arguments:
    flag -- the flag for which to return a value
    content -- the content of the command

    Keyword arguments:
    default -- the value to return in case the flag is not present in the content, or the flag has no associated value (last argument)
    """
    if not has_flag(flag, content):
        return default

    args = content.split()
    i = args.index("-" + flag)

    # get argument following flag
    if i + 1 == len(args):
        return default
    return args[i + 1]


def user_from_mention(client, mention):
    match = re.match("<@!?(\d+)>", mention)
    if match is None:
        return None
    else:
        return client.get_user(int(match.group(1)))


def sanitized(msg):
    return msg.replace("`", "'")


def get_correct_attr(obj, attr, client):
    if not client.config["ENABLE_COURSES"] and hasattr(obj, f"{attr}_no_courses"):
        return getattr(obj, f"{attr}_no_courses")
    elif hasattr(obj, attr):
        return getattr(obj, attr)
    else:
        return None


# prints a traceback and sends it to discord
# to get a traceback sent to steam put this line in any except: call
# await utils.sendTraceback(client, "")
async def sendTraceback(client, content=""):
    # print the traceback to the terminal
    print(content)
    print(traceback.format_exc())

    # if there is a traceback server and channel, send the traceback in discord as well
    try:
        msg_to_send = f"```bash\n{traceback.format_exc()}\n```"
        if content:
            msg_to_send = f"`{content}`\n" + msg_to_send
        await client.TRACEBACK_CHANNEL.send(msg_to_send)
    except:
        print(
            "\nNote: traceback was not sent to Discord, if you want this double check your config.json"
        )


# Global http session
http_session = None


def initialize_http(loop):
    global http_session
    http_session = aiohttp.ClientSession(loop=loop)


def get_aiohttp():
    return http_session


def get_user_divider(client, user_id: int) -> str:
    user_hash = hash(f"{user_id} {client.config['SERVER_ID']}")

    DIVIDER_CHARACTERS = client.config["smc_chars"]
    DIVIDER_MIN_LEN = client.config["smc_div_min_len"]
    DIVIDER_MAX_LEN = client.config["smc_div_max_len"]

    divider_char_idx = user_hash % (len(DIVIDER_CHARACTERS) - 1)
    divider_len = user_hash % (DIVIDER_MAX_LEN - DIVIDER_MIN_LEN)
    return DIVIDER_CHARACTERS[divider_char_idx] * (divider_len + DIVIDER_MIN_LEN)


def is_divider(client, divider: str) -> bool:
    DIVIDER_CHARACTERS = client.config["smc_chars"]

    c = divider[0]
    return c in DIVIDER_CHARACTERS and all([c == char for char in divider])
