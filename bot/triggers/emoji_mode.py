# THIS FILE ONLY HANDLES MESSAGE INTERACTION (DEALING WITH AND RESPONDING TO
# MESSAGES VIOLATING THE EMOJI-MODE STATUS)
#
# PLEASE SEE `commands/emoji_mode.py` FOR MODIFYING THE EMOJI-MODE STATE

from . import utils
import emoji
import random
import re
import requests

from discord import ChannelType

# emotes are of the form <:emote_name:1234> where `1234` is the emote's id
discord_emote_re = re.compile("<:[^:]+:(\d+)>")
discord_emote_animated_re = re.compile("<a:[^:]+:(\d+)>")
discord_emote_id_re = re.compile(":(\d+)>")

invalid_emoji_re = re.compile("🇦|🇧|🇨|🇩|🇪|🇫|🇬|🇮|🇯|🇰|🇱|🇲|🇳|🇴|🇵|🇷|🇸|🇹|🇺|🇻|🇼|🇽|🇾|🇿|🇶")

# explains to the violator why their message was deleted
async def send_message_to_violator(client, user):
    await user.send(client.messages["emoji_mode_dm"])


# validates a single discord emote by verifying that its id is a real emote
# id. if the emote is valid, it will return an empty string to remove the
# emote from the message content.  If the emote is invalid, the content string
# will be unmodified.
def validate_discord_emote(emote) -> str:
    emote_id = discord_emote_id_re.search(str(emote)).group(1)
    if requests.get(f"https://cdn.discordapp.com/emojis/{emote_id}").status_code == 200:
        # valid emote
        return ""
    else:
        # invalid emote
        return emote


# returns true if the message only contains emoji and whitespace.  It will
# validate discord emotes as well.
def valid_emoji(content, msg) -> bool:
    if len(msg.embeds) or len(msg.attachments):
        return False

    content = discord_emote_re.sub(validate_discord_emote, content)
    content = discord_emote_animated_re.sub(validate_discord_emote, content)
    content = invalid_emoji_re.sub("a", content)
    content = emoji.get_emoji_regexp().sub("", content)

    return len(content.split()) == 0  # calling split() discounts whitepace


# deletes message if the message is invalid
# returns true if the message was deleted
async def invalid_emoji_message(client, msg) -> bool:
    if msg.channel.type is ChannelType.private or msg.channel.type is ChannelType.group:
        return False

    hits = 0

    async with client.lock:
        client.c.execute(
            f"SELECT count(*) FROM emoji_channels WHERE channel_id = {msg.channel.id}"
        )
        hits += client.c.fetchone()[0]

    async with client.lock:
        client.c.execute(
            f"SELECT count(*) FROM emoji_users WHERE user_id = {msg.author.id}"
        )
        hits += client.c.fetchone()[0]

    if hits > 0:
        if utils.user_is_mod(client, msg.author):
            return False

        if not valid_emoji(msg.content, msg):
            await msg.delete()
            await send_message_to_violator(client, msg.author)
            return True
    return False
