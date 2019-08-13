from .commands.help import Help
from .commands import all_commands
from .welcome import Welcome
from .commands.class_management import AddClass, RemoveClass

msg_triggers = [Help()]
msg_triggers.extend(all_commands)

new_member_triggers = [Welcome()]

reaction_triggers = [AddClass(), RemoveClass()]
