class MessageTrigger:
    async def execute_message(self, client, msg, idx):
        raise NotImplementedError(
            "'execute_message' is not implemented for this message trigger"
        )

    async def get_trigger_score(self, client, msg):
        raise NotImplementedError(
            "'get_trigger_score' is not implemented for this message trigger"
        )
