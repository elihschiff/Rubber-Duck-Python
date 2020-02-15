from .commands.help import Help
from .commands import all_commands
from .welcome import Welcome
from .commands.connectfour import ConnectFour
from .commands.tictactoe import TicTacToe
from .commands.rps import RockPaperScissors

msg_triggers = [Help()]
msg_triggers.extend(all_commands)

new_member_triggers = [Welcome()]

reaction_triggers = [
    ConnectFour(),
    RockPaperScissors(),
    TicTacToe(),
]
