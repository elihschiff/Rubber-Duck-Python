class NewMemberTrigger:
    async def execute_new_member(self, client, member) -> bool:
        raise NotImplementedError(
            "'execute' is not implemented for this new member trigger"
        )
