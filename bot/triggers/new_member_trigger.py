import discord

from ..duck import DuckClient


class NewMemberTrigger:
    async def execute_new_member(
        self, client: DuckClient, member: discord.Member
    ) -> None:
        raise NotImplementedError(
            "'execute' is not implemented for this new member trigger"
        )
