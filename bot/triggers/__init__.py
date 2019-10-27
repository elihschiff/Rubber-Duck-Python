from .commands.help import Help
from .commands import all_commands
from .welcome import Welcome
from .commands.class_management import AddClass, RemoveClass
<<<<<<< HEAD
from .commands.connectfour import ConnectFour
from .commands.tictactoe import TicTacToe
from .commands.rps import RockPaperScissors
=======
from .pdf_to_png import PdfToPng
>>>>>>> a0073225ea5dec79c2c077823a364291a8836380

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
