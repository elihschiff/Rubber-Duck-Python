from typing import List

from .commands import ALL_COMMANDS, Command
from .commands.class_management import AddClass, RemoveClass
from .commands.connectfour import ConnectFour
from .commands.delete import Delete
from .commands.help import Help
from .commands.tictactoe import TicTacToe
from .commands.rps import RockPaperScissors
from .welcome import Welcome

from .new_member_trigger import NewMemberTrigger
from .reaction_trigger import ReactionTrigger

MSG_TRIGGERS: List[Command] = [Help()]
MSG_TRIGGERS.extend(ALL_COMMANDS)

NEW_MEMBER_TRIGGERS: List[NewMemberTrigger] = [Welcome()]

REACTION_TRIGGERS: List[ReactionTrigger] = [
    AddClass(),
    ConnectFour(),
    Delete(),
    RockPaperScissors(),
    TicTacToe(),
    RemoveClass(),
]
