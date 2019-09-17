from .commands.help import Help
from .commands import all_commands
from .welcome import Welcome
from .commands.class_management import AddClass, RemoveClass
from .commands.games import ConnectFour
from .commands.tictactoe import TicTacToe

msg_triggers = [Help()]
msg_triggers.extend(all_commands)

new_member_triggers = [Welcome()]

reaction_triggers = [AddClass(), ConnectFour(), TicTacToe(), RemoveClass()]
