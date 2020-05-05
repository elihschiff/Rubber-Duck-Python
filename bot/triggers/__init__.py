from .commands.help import Help
from .commands import ALL_COMMANDS
from .commands.delete import Delete
from .welcome import Welcome
from .commands.class_management import AddClass, RemoveClass
from .commands.connectfour import ConnectFour
from .commands.tictactoe import TicTacToe
from .commands.rps import RockPaperScissors

MSG_TRIGGERS = [Help()]
MSG_TRIGGERS.extend(ALL_COMMANDS)

NEW_MEMBER_TRIGGERS = [Welcome()]

REACTION_TRIGGERS = [
    AddClass(),
    ConnectFour(),
    Delete(),
    RockPaperScissors(),
    TicTacToe(),
    RemoveClass(),
]
