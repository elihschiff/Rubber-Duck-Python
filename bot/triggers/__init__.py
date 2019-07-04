class MessageTrigger:
    async def execute(self, client, msg) -> bool:
        raise NotImplementedError("'execute' is not implemented for this trigger")


from .commands.echo import Echo

msg_triggers = [Echo()]
