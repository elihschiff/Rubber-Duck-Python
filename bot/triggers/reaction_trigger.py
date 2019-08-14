class ReactionTrigger:
    async def execute_reaction(self, client, reaction, user) -> bool:
        raise NotImplementedError(
            "'execute' is not implemented for this reaction trigger"
        )
