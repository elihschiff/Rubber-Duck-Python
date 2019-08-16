import time
import asyncio
import discord


async def delay_send(sendable, msg, delay_factor=1.0, embed=None):
    delay = (0.5 + 0.003 * len(msg)) * delay_factor
    # print(delay)
    delay = max(2, delay)

    delay = 0

    async with sendable.typing():
        await asyncio.sleep(delay)

    return await sendable.send(msg, embed=embed)


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


def user_is_admin(user) -> bool:
    try:
        return user.guild_permissions.administrator
    except:
        return False
