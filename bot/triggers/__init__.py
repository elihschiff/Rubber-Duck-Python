class MessageTrigger:
    async def execute(self, client, msg) -> bool:
        raise NotImplementedError("'execute' is not implemented for this trigger")


from .commands.help import Help

from .commands import all_commands

msg_triggers = [Help()]
msg_triggers.extend(all_commands)
