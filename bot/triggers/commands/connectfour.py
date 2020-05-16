import random
import re
from typing import Any, cast, Dict, List, Match, Optional, Tuple

import discord

from .games import Game, get_game_footer
from .. import utils
from ..reaction_trigger import ReactionTrigger
from ...duck import DuckClient

COLUMNS = [
    {"emoji": "0\u20E3", "name": ":zero:"},
    {"emoji": "1\u20E3", "name": ":one:"},
    {"emoji": "2\u20E3", "name": ":two:"},
    {"emoji": "3\u20E3", "name": ":three:"},
    {"emoji": "4\u20E3", "name": ":four:"},
    {"emoji": "5\u20E3", "name": ":five:"},
    {"emoji": "6\u20E3", "name": ":six:"},
    {"emoji": "7\u20E3", "name": ":seven:"},
    {"emoji": "8\u20E3", "name": ":eight:"},
    {"emoji": "9\u20E3", "name": ":nine:"},
    {"emoji": "\U0001F51F", "name": ":keycap_ten:"},
    *[
        {
            "emoji": chr(0x1F1E6 + i),
            "name": ":regional_indicator_" + chr(ord("a") + i) + ":",
        }
        for i in range(9)
    ],
]


class ConnectFour(Game, ReactionTrigger):
    names = ["c4", "connect4", "connectfour"]
    description = "Begins a Connect Four game with another player(s)"
    usage = "!c4 [@ another player] [(optional) -r rows] [(optional) -c columns]"
    examples = "!c4 @myfriend, !c4 @myfriend -r 3 -c 4"
    notes = (
        "Maximum of eight players.  Default dimensions is 6x7, but can go up to 10x15."
    )

    class Game:
        def __init__(
            self,
            players: Optional[List[Dict[str, Any]]] = None,
            board: Optional[List[List[int]]] = None,
        ) -> None:
            self.players = cast(List[Dict[str, Any]], players)
            self.board = cast(List[List[int]], board)

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
                                "user": utils.user_from_mention(client, player[1]),
                            }
                        )
                    break

            # construct player map for faster index lookup, maps piece to player index
            pieces = {":black_circle:": -1}
            for (i, player) in enumerate(self.players):
                pieces[player["piece"]] = i

            self.board = embed.description.split("\n")[1:-1]  # type: ignore
            for row in self.board:
                for (piece, i) in pieces.items():
                    row = row.replace(piece, chr(i + 1))  # type: ignore
                row = [ord(c) - 1 for c in row]  # type: ignore

            if msg.content == "Draw!":
                return
            mention = cast(Match[str], re.search(r"<@!?(\d+)>", msg.content))

            user = [
                i
                for (i, player) in enumerate(self.players)
                if player["user"].id == int(mention.group(1))
            ][0]

            if msg.content.endswith(" has won!"):
                self.winner = user
            else:
                self.turn = user

        def is_draw(self) -> bool:
            for row in self.board:
                if -1 in row:
                    return False
            return True

        def get_content(self) -> str:
            if self.winner == -1:
                if self.is_draw():
                    return "Draw!"
                else:
                    return f"It's {self.players[self.turn]['user'].mention}'s turn."
            else:
                return f"{self.players[self.winner]['user'].mention} has won!"

        def get_piece(self, player: int) -> Any:
            if player == -1:
                return ":black_circle:"
            return self.players[player]["piece"]

        def get_embed(self, footer: str) -> discord.Embed:
            board = self.board
            for row in board:
                for cell in row:
                    cell = self.get_piece(cell)

            embed = discord.Embed(
                title="Connect Four",
                description="\n".join(
                    [
                        "".join([col["name"] for col in COLUMNS[: len(self.board[0])]]),
                        "\n".join(["".join(row) for row in board]),  # type: ignore
                        "".join([col["name"] for col in COLUMNS[: len(self.board[0])]]),
                    ]
                ),
            )
            embed.add_field(
                name="Players",
                value=" vs. ".join(
                    [
                        player["piece"] + " " + player["user"].mention
                        for player in self.players
                    ]
                ),
            )
            embed.set_footer(text=footer)

            return embed

        def in_board(self, pos: Tuple[int, int]) -> bool:
            return (
                pos[0] >= 0
                and pos[1] >= 0
                and pos[0] < len(self.board)
                and pos[1] < len(self.board[pos[0]])
            )

        def nearby_winner(self, pos: Tuple[int, int]) -> None:
            player = self.board[pos[0]][pos[1]]

            directions = [(1, 0), (1, 1), (0, 1), (-1, 1)]
            for direction in directions:
                length = 1

                peek = (pos[0] + direction[0], pos[1] + direction[1])
                while self.in_board(peek) and self.board[peek[0]][peek[1]] == player:
                    length += 1
                    peek = (peek[0] + direction[0], peek[1] + direction[1])

                peek = (pos[0] - direction[0], pos[1] - direction[1])
                while self.in_board(peek) and self.board[peek[0]][peek[1]] == player:
                    length += 1
                    peek = (peek[0] - direction[0], peek[1] - direction[1])

                if length >= 4:
                    self.winner = player

        def take_turn(self, col: int) -> Optional[Tuple[int, int]]:
            if self.winner != -1:
                return None
            if self.board[0][col] != -1:
                return None
            row = 0
            while row + 1 < len(self.board) and self.board[row + 1][col] == -1:
                row += 1
            self.board[row][col] = self.turn
            self.turn = (self.turn + 1) % len(self.players)

            self.nearby_winner((row, col))

            return (row, col)

    # TODO: rewrite this to not need linter disabling
    # pylint: disable=too-many-return-statements
    async def execute_command(
        self, client: DuckClient, msg: discord.Message, content: str
    ) -> None:
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        pieces = (
            client.config["connectfour"]["pieces"]
            if "pieces" in client.config["connectfour"]
            else [":red_circle:", ":blue_circle:", ":white_circle:"]
        )

        players = list(set([*msg.mentions, msg.author]))

        if len(players) < 2:
            await utils.delay_send(
                msg.channel, client.messages["connectfour_err_no_opponent"]
            )
            return
        max_players = min(client.config["connectfour"]["max_players"], len(pieces))
        if len(players) > max_players:
            await utils.delay_send(
                msg.channel,
                client.messages["connectfour_err_players"].format(max_players),
            )
            return

        # make sure the tagged player is not a bot
        for player in players:
            if player.bot:
                await utils.delay_send(
                    msg.channel, client.messages["connectfour_err_bot_player"]
                )
                return
        random.shuffle(players)
        players_dict_list = [
            {"piece": pieces[i], "user": player} for (i, player) in enumerate(players)
        ]

        rows_str = cast(str, utils.get_flag("r", content, "6"))
        if not rows_str.isdigit() or int(rows_str) < 1:
            await utils.delay_send(msg.channel, client.messages["connectfour_err_num"])
            return
        rows = int(rows_str)
        max_rows = client.config["connectfour"]["max_rows"]
        if rows > max_rows:
            await utils.delay_send(
                msg.channel,
                client.messages["connectfour_err_max_rows"].format(max_rows),
            )
            return

        cols_str = cast(str, utils.get_flag("c", content, "7"))
        if not cols_str.isdigit() or int(cols_str) < 1:
            await utils.delay_send(msg.channel, client.messages["connectfour_err_num"])
            return
        cols = int(cols_str)
        max_cols = min(client.config["connectfour"]["max_cols"], len(COLUMNS))
        if cols > max_cols:
            await utils.delay_send(
                msg.channel,
                client.messages["connectfour_err_max_cols"].format(max_cols),
            )
            return

        game = ConnectFour.Game(
            players_dict_list, [[-1 for c in range(cols)] for r in range(rows)]
        )
        msg = await utils.delay_send(
            msg.channel,
            game.get_content(),
            embed=game.get_embed(get_game_footer(client)),
        )
        for col in COLUMNS[:cols]:
            await msg.add_reaction(col["emoji"])

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
        if len(msg.embeds) == 0 or msg.embeds[0].title != "Connect Four":
            return False

        await msg.remove_reaction(
            reaction.emoji, cast(discord.User, client.get_user(reaction.user_id))
        )

        game = ConnectFour.Game()
        game.parse_msg(msg, client)

        cols = [col["emoji"] for col in COLUMNS[: len(game.board[0])]]
        if reaction.emoji.name not in cols:
            return False
        if reaction.user_id != game.players[game.turn]["user"].id:
            return False
        pos = game.take_turn(cols.index(reaction.emoji.name))
        if pos is None:
            return False

        if pos[0] == 0:
            await msg.remove_reaction(reaction.emoji, client.user)

        reactions_to_add = [reaction for reaction in msg.reactions if reaction.me]
        await msg.delete()

        new_msg = await utils.delay_send(
            channel, game.get_content(), embed=game.get_embed(get_game_footer(client)),
        )

        for add_reaction in reactions_to_add:
            await new_msg.add_reaction(add_reaction)

        return True
