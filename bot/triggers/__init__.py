from .commands.help import Help
from .commands import all_commands
from .commands.delete import Delete
from .welcome import Welcome
from .commands.class_management import AddClass, RemoveClass
from .commands.connectfour import ConnectFour
from .commands.tictactoe import TicTacToe
from .commands.rps import RockPaperScissors

msg_triggers = [Help()]
msg_triggers.extend(all_commands)

new_member_triggers = [Welcome()]

reaction_triggers = [
    AddClass(),
    ConnectFour(),
    Delete(),
    RockPaperScissors(),
    TicTacToe(),
    RemoveClass(),
]
