import random
import re
from typing import cast, Dict, List, Optional, Tuple, Union

import discord

from .games import Game, get_game_footer
from .. import utils
from ..reaction_trigger import ReactionTrigger
from ...duck import DuckClient

POSITIONS = [
    {"emoji": "1\u20E3", "name": ":one:"},
    {"emoji": "2\u20E3", "name": ":two:"},
    {"emoji": "3\u20E3", "name": ":three:"},
    {"emoji": "4\u20E3", "name": ":four:"},
    {"emoji": "5\u20E3", "name": ":five:"},
    {"emoji": "6\u20E3", "name": ":six:"},
    {"emoji": "7\u20E3", "name": ":seven:"},
    {"emoji": "8\u20E3", "name": ":eight:"},
    {"emoji": "9\u20E3", "name": ":nine:"},
]


def in_board(pos: Tuple[int, int]) -> bool:
    return 0 <= pos[0] < 3 and 0 <= pos[1] < 3


class TicTacToe(Game, ReactionTrigger):
    names = ["ttt", "tictactoe"]
    description = "Begins a game of Tic Tac Toe with a player."
    usage = "!ttt [@ another user]"

    class Game:
        def __init__(
            self,
            players: Optional[List[Dict[str, Union[int, discord.User]]]] = None,
            board: Optional[List[List[Union[int, str]]]] = None,
        ):
            # do the casting here so we don't have to deal with it later
            self.players = cast(List[Dict[str, Union[int, discord.User]]], players)
            self.board = cast(List[List[Union[int, str]]], board)
            # new
            self.pieces = {
                -1: ":one:",
                -2: ":two:",
                -3: ":three:",
                -4: ":four:",
                -5: ":five:",
                -6: ":six:",
                -7: ":seven:",
                -8: ":eight:",
                -9: ":nine:",
            }

            self.turn = 0
            self.winner = -1

        def parse_msg(self, msg: discord.Message, client: DuckClient) -> None:
            embed = msg.embeds[0]

            for field in embed.fields:
                if field.name == "Players":  # type: ignore
                    self.players = []
                    for player in field.value.split(" vs. "):  # type: ignore
                        player = player.split()
                        self.players.append(
                            {
                                "piece": player[0],
                                "user": cast(
                                    discord.User,
                                    utils.user_from_mention(client, player[1]),
                                ),
                            }
                        )
                    break

            # construct player map for faster index lookup, maps piece to player index

            # pieces = {":black_circle:": -1}
            # new
            pieces = {
                -1: ":one:",
                -2: ":two:",
                -3: ":three:",
                -4: ":four:",
                -5: ":five:",
                -6: ":six:",
                -7: ":seven:",
                -8: ":eight:",
                -9: ":nine:",
            }
            for (i, player) in enumerate(self.players):
                pieces[i] = player["piece"]

            self.board = embed.description.split("\n")  # type: ignore

            for row_idx in range(3):
                row = self.board[row_idx]
                for (i, piece) in pieces.items():
                    row = row.replace(piece, chr(i + 9))  # type: ignore
                # TODO: what does the next line do?
                self.board[row_idx] = [ord(c) - 9 for c in row]  # type: ignore

            if msg.content == "Draw!":
                return

            mention = re.search(r"<@!?(\d+)>", msg.content)

            users = []
            for (i, player) in enumerate(self.players):
                if player["user"].id == int(mention.group(1)):  # type: ignore
                    users.append(i)
            user = users[0]

            if msg.content.endswith(" has won!"):
                self.winner = user
            else:
                self.turn = user

        def is_draw(self) -> bool:
            for row in self.board:
                for element in row:
                    if int(element) < 0:
                        return False
            return True

        def get_content(self) -> str:
            if self.winner == -1:
                if self.is_draw():
                    return "Draw!"
                else:
                    return f"It's {self.players[self.turn]['user'].mention}'s turn."  # type: ignore
            else:
                return f"{self.players[self.winner]['user'].mention} has won!"  # type: ignore

        def get_piece(self, player: int) -> Union[int, str]:
            # if player == -1:
            #     return ":black_large_square:"
            if player < 0:
                return self.pieces[player]
            return cast(int, self.players[player]["piece"])

        def get_embed(self, footer: str) -> discord.Embed:
            board = self.board
            for row_idx in range(3):
                for col_idx in range(3):
                    board[row_idx][col_idx] = self.get_piece(
                        cast(int, board[row_idx][col_idx])
                    )

            embed = discord.Embed(
                title="Tic Tac Toe",
                description="\n".join(["\n".join(["".join(row) for row in board])]),  # type: ignore
            )
            embed.add_field(
                name="Players",
                value=" vs. ".join(
                    [
                        player["piece"] + " " + player["user"].mention  # type: ignore
                        for player in self.players
                    ]
                ),
            )
            embed.set_footer(text=footer)

            return embed

        # TODO: rewrite this to not need linter disabling
        # pylint: disable=too-many-branches
        def check_for_winner(self) -> None:
            # check horizontals
            for i in range(3):
                end = True
                for j in range(3):
                    if self.board[i][j] != self.turn:
                        end = False
                        break
                if end:
                    self.winner = self.turn
                    return
            # check verticals
            for i in range(3):
                end = True
                for j in range(3):
                    if self.board[j][i] != self.turn:
                        end = False
                        break
                if end:
                    self.winner = self.turn
                    return
            # diagonal
            end = True
            for i in range(3):
                if self.board[i][i] != self.turn:
                    end = False
                    break
            if end:
                self.winner = self.turn
                return
            # anti diagonal
            end = True
            for i in range(3):
                if self.board[2 - i][i] != self.turn:
                    end = False
                    break
            if end:
                self.winner = self.turn
                return

        def take_turn(self, pos: int) -> Optional[int]:
            if self.winner != -1:
                return None
            if self.board[pos // 3][pos % 3] >= 0:  # type: ignore
                return None

            self.board[pos // 3][pos % 3] = self.turn

            self.check_for_winner()
            self.turn = (self.turn + 1) % 2

            return pos

    # this is called when a message starting with "!commandname" is run
    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        pieces = [":x:", ":o:"]

        players = list(set([*msg.mentions, msg.author]))
        if len(players) != 2:
            await utils.delay_send(
                msg.channel, client.messages["tictactoe_err_num_players"]
            )
            return

        # make sure the tagged player is not a bot
        for player in players:
            if player.bot:
                await utils.delay_send(
                    msg.channel, client.messages["tictactoe_err_bot_player"]
                )
                return

        random.shuffle(players)

        players = [
            {"piece": pieces[i], "user": player} for (i, player) in enumerate(players)  # type: ignore
        ]

        game = TicTacToe.Game(
            # note we can't use [] * 3 otherwise it creates a deep copy
            players,  # type: ignore
            [[-1 - c - 3 * r for c in range(3)] for r in range(3)],
        )

        msg = await utils.delay_send(
            msg.channel,
            game.get_content(),
            embed=game.get_embed(get_game_footer(client)),
        )

        for spot in POSITIONS[:9]:
            await msg.add_reaction(spot["emoji"])

    async def execute_reaction(
        self,
        client: DuckClient,
        reaction: discord.RawReactionActionEvent,
        channel: discord.TextChannel,
        msg: discord.Message,
        user: discord.User,
    ) -> bool:
        if client.user.id == reaction.user_id:
            return False

        # channel = await client.fetch_channel(reaction.channel_id)
        # msg = await channel.fetch_message(reaction.message_id)
        if len(msg.embeds) == 0 or msg.embeds[0].title != "Tic Tac Toe":
            return False

        await msg.remove_reaction(reaction.emoji, client.get_user(reaction.user_id))  # type: ignore

        game = TicTacToe.Game()
        game.parse_msg(msg, client)

        positions = [spot["emoji"] for spot in POSITIONS[:9]]

        if reaction.emoji.name not in positions:
            return False
        if reaction.user_id != game.players[game.turn]["user"].id:  # type: ignore
            return False
        pos = game.take_turn(positions.index(reaction.emoji.name))
        if pos is None:
            return False

        await msg.clear_reaction(reaction.emoji)

        reactions_to_add = [reaction for reaction in msg.reactions if reaction.me]
        await msg.delete()

        if game.winner != -1 or game.is_draw():
            reactions_to_add = []

        new_msg = await utils.delay_send(
            channel, game.get_content(), embed=game.get_embed(get_game_footer(client)),
        )

        for add_reaction in reactions_to_add:
            await new_msg.add_reaction(add_reaction)

        return True
