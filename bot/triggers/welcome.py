from typing import cast

import discord

from .new_member_trigger import NewMemberTrigger
from ..duck import DuckClient


class Welcome(NewMemberTrigger):
    async def execute_new_member(
        self, client: DuckClient, member: discord.Member
    ) -> None:
        welcome_channel = client.get_channel(client.config["welcome_channel_id"])
        welcome_channel = cast(discord.TextChannel, welcome_channel)
        if welcome_channel:
            await welcome_channel.send(
                client.messages["welcome_public"].format(member.mention)
            )

        if client.config["ENABLE_COURSES"]:
            non_all_seer = client.server.get_role(client.config["non_all_seer_id"])
            non_all_seer_snowflake = cast(discord.abc.Snowflake, non_all_seer)
            await member.add_roles(non_all_seer_snowflake)

            await member.send(client.messages["welcome_dm"])
