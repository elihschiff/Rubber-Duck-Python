from typing import Optional, Tuple

import discord

from ..duck import DuckClient


class MessageTrigger:
    async def execute_message(
        self, client: DuckClient, msg: discord.Message, idx: int
    ) -> None:
        raise NotImplementedError(
            "'execute_message' is not implemented for this message trigger"
        )

    async def get_trigger_score(
        self, client: DuckClient, msg: discord.Message
    ) -> Tuple[float, Optional[int]]:
        raise NotImplementedError(
            "'get_trigger_score' is not implemented for this message trigger"
        )
