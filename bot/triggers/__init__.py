from .commands.help import Help
from .commands import all_commands
from .welcome import Welcome
from .commands import class_management

msg_triggers = [Help()]
msg_triggers.extend(all_commands)

new_member_triggers = [Welcome()]

reaction_triggers = [class_management.AddClass()]
