# THIS FILE ONLY HANDLES MESSAGE INTERACTION (DEALING WITH AND RESPONDING TO
# MESSAGES VIOLATING THE EMOJI-MODE STATUS)
#
# PLEASE SEE `commands/emoji_mode.py` FOR MODIFYING THE EMOJI-MODE STATE

from . import utils
import emoji
import random
import re
import requests

from nextcord import ChannelType

# emotes are of the form <:emote_name:1234> where `1234` is the emote's id
discord_emote_re = re.compile("<a?:[\w]+?:(\d+?)>")
discord_emote_id_re = re.compile(":(\d+)>")
nested_emote_re = re.compile("<[^>]+<")

invalid_emoji_re = re.compile(
    "🇦|🇧|🇨|🇩|🇪|🇫|🇬|🇮|🇯|🇰|🇱|🇲|🇳|🇴|🇵|🇷|🇸|🇹|🇺|🇻|🇼|🇽|🇾|🇿|🇶|:regional_indicator_[a-zA-Z]+?:"
)

# explains to the violator why their message was deleted
async def send_message_to_violator(client, user, message):
    try:
        await user.send(message)
    except HTTPException:
        pass


# validates a single discord emote by verifying that its id is a real emote
# id. if the emote is valid, it will return an empty string to remove the
# emote from the message content.  If the emote is invalid, the content string
# will be unmodified.
def validate_discord_emote(emote) -> str:
    emote_id = discord_emote_id_re.search(str(emote)).group(1)
    res = requests.get(f"https://cdn.discordapp.com/emojis/{emote_id}", timeout=2)
    if res.status_code == 200:
        # valid emote
        return ""
    else:
        # invalid emote
        return emote


# returns true if the message only contains emoji and whitespace.  It will
# validate discord emotes as well.
def valid_emoji(content, msg) -> bool:
    if msg.embeds or msg.attachments:
        return False

    if nested_emote_re.match(content):
        return True

    content = discord_emote_re.sub(validate_discord_emote, content)
    content = invalid_emoji_re.sub("a", content)
    content = emoji.get_emoji_regexp().sub("", content)

    return len(content.split()) == 0  # calling split() discounts whitepace


# returns true if the message contains any emoji.
def contains_emoji(content) -> bool:
    return bool(
        discord_emote_re.match(content) or emoji.get_emoji_regexp().match(content)
    )


# deletes message if the message is invalid
# returns true if the message was deleted
async def invalid_emoji_message(client, msg) -> bool:
    if msg.channel.type is ChannelType.private or msg.channel.type is ChannelType.group:
        return False

    hits = 0

    # Check for emoji mode
    async with client.lock:
        client.c.execute(
            "SELECT count(*) FROM emoji_channels WHERE channel_id = :chann_id",
            {"chann_id": msg.channel.id},
        )
        hits += client.c.fetchone()[0]

    async with client.lock:
        client.c.execute(
            "SELECT count(*) FROM emoji_users WHERE user_id = :author_id",
            {"author_id": msg.author.id},
        )
        hits += client.c.fetchone()[0]

    if hits > 0:
        if utils.user_is_mod(client, msg.author):
            return False

        if not valid_emoji(msg.content, msg):
            await msg.delete()
            await send_message_to_violator(
                client, msg.author, client.messages["emoji_mode_dm"]
            )
            return True

    hits = 0

    # check for unemoji mode
    async with client.lock:
        client.c.execute(
            "SELECT count(*) FROM unemoji_channels WHERE channel_id = :chann_id",
            {"chann_id": msg.channel.id},
        )
        hits += client.c.fetchone()[0]

    async with client.lock:
        client.c.execute(
            "SELECT count(*) FROM unemoji_users WHERE user_id = :author_id",
            {"author_id": msg.author.id},
        )
        hits += client.c.fetchone()[0]

    if hits > 0:
        if utils.user_is_mod(client, msg.author):
            return False

        if contains_emoji(msg.content):
            await msg.delete()
            await send_message_to_violator(
                client, msg.author, client.messages["unemoji_mode_dm"]
            )
            return True
    return False
