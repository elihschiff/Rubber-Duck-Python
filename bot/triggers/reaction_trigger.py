import discord

from ..duck import DuckClient


class ReactionTrigger:
    async def execute_reaction(
        self,
        client: DuckClient,
        reaction: discord.RawReactionActionEvent,
        channel: discord.TextChannel,
        msg: discord.Message,
        user: discord.User,
    ) -> bool:
        raise NotImplementedError(
            "'execute' is not implemented for this reaction trigger"
        )
