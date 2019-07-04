class MessageTrigger:
    async def execute(self, msg):
        raise NotImplementedError("'execute' is not implemented for this trigger")


from .commands.echo import Echo

msg_triggers = [Echo()]
