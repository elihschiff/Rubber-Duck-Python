from .commands.help import Help
from .commands import all_commands
from .welcome import Welcome
from .commands.class_management import AddClass, RemoveClass
from .commands.connectfour import ConnectFour
from .commands.tictactoe import TicTacToe
from .commands.rps import RockPaperScissors

msg_triggers = [Help(), PdfToPng()]
msg_triggers.extend(all_commands)

new_member_triggers = [Welcome()]

reaction_triggers = [
    AddClass(),
    ConnectFour(),
    RockPaperScissors(),
    TicTacToe(),
    RemoveClass(),
]
