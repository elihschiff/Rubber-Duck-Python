class MessageTrigger:
    async def execute_message(self, client, msg) -> bool:
        raise NotImplementedError(
            "'execute' is not implemented for this message trigger"
        )
