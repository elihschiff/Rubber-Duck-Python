class MessageTrigger:
    async def execute(self, client, msg) -> bool:
        raise NotImplementedError("'execute' is not implemented for this trigger")


from .commands.help import Help
from .commands import all_commands

msg_triggers = [Help()]
msg_triggers.extend(all_commands)


class NewMemberTriggers:
    async def execute(self, client, member) -> bool:
        raise NotImplementedError("'execute' is not implemented for this trigger")


from .welcome import Welcome

new_member_triggers = [Welcome()]
