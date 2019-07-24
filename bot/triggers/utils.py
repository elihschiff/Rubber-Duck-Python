import time
import asyncio
import discord


async def delay_send(channel, msg, delay_factor=1.0, embed=None):
    delay = (0.5 + 0.003 * len(msg)) * delay_factor
    # print(delay)
    delay = max(2, delay)

    async with channel.typing():
        await asyncio.sleep(delay)

    return await channel.send(msg, embed=embed)


async def generate_react_menu(
    msg, user_id, opening_message, max_length, option_list, cancel_message
):
    emojiNumbers = [
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
    max_length = min(max_length, len(emojiNumbers))
    noMatchingResultsEmote = "🚫"

    msgToSend = f"<@{user_id}>"
    msgToSend += opening_message
    for i in range(min(max_length, len(option_list))):
        msgToSend += f"\n\n{emojiNumbers[i]} {option_list[i]}"
    msgToSend += f"\n\n{noMatchingResultsEmote} {cancel_message}"
    sentMsg = await msg.channel.send(msgToSend)
    for i in range(min(max_length, len(option_list))):
        await sentMsg.add_reaction(emojiNumbers[i])
    await sentMsg.add_reaction(noMatchingResultsEmote)


def user_is_admin(user) -> bool:
    return user.guild_permissions.administrator
