from .games import Game
from .. import utils
from ..reaction_trigger import ReactionTrigger

import discord
import re

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


class TicTacToe(Game, ReactionTrigger):
    names = ["ttt", "tictactoe"]
    description = "Begins a game of Tic Tac Toe with a player."
    needsContent = True

    class Game:
        def __init__(self, players=None, board=None):
            self.players = players
            self.board = board
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

        def parse_msg(self, msg, client):
            embed = msg.embeds[0]

            for field in embed.fields:
                if field.name == "Players":
                    self.players = []
                    for player in field.value.split(" vs. "):
                        player = player.split()
                        self.players.append(
                            {
                                "piece": player[0],
                                "user": utils.user_from_mention(client, player[1]),
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

            self.board = embed.description.split("\n")

            for r in range(3):
                row = self.board[r]
                for (i, piece) in pieces.items():
                    row = row.replace(piece, chr(i + 9))
                self.board[r] = [ord(c) - 9 for c in row]

            if msg.content == "Draw!":
                return

            mention = re.search("<@!?(\d+)>", msg.content)

            user = []
            for (i, player) in enumerate(self.players):
                if player["user"].id == int(mention.group(1)):
                    user.append(i)
            user = user[0]

            if msg.content.endswith(" has won!"):
                self.winner = user
            else:
                self.turn = user

        def is_draw(self):
            for row in self.board:
                for element in row:
                    if element < 0:
                        return False
            return True

        def get_content(self):
            if self.winner == -1:
                if self.is_draw():
                    return "Draw!"
                else:
                    return f"It's {self.players[self.turn]['user'].mention}'s turn."
            else:
                return f"{self.players[self.winner]['user'].mention} has won!"

        def get_piece(self, player):
            # if player == -1:
            #     return ":black_large_square:"
            if player < 0:
                return self.pieces[player]
            return self.players[player]["piece"]

        def get_embed(self, footer):
            board = self.board
            for r in range(3):
                for c in range(3):
                    board[r][c] = self.get_piece(board[r][c])

            embed = discord.Embed(
                title="Tic Tac Toe",
                description="\n".join(["\n".join(["".join(row) for row in board])]),
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

        def in_board(self, pos):
            return pos[0] >= 0 and pos[1] >= 0 and pos[0] < 3 and pos[1] < 3

        def check_for_winner(self, pos):
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
            if pos == 0 or pos == 8:
                end = True
                for i in range(3):
                    if self.board[i][i] != self.turn:
                        end = False
                        break
                if end:
                    self.winner = self.turn
                    return
            # anti diagonal
            if pos == 2 or pos == 6:
                end = True
                for i in range(3):
                    if self.board[2 - i][i] != self.turn:
                        end = False
                        break
                if end:
                    self.winner = self.turn
                    return

        def take_turn(self, pos):
            if self.winner != -1:
                return None
            if self.board[pos // 3][pos % 3] >= 0:
                return None

            self.board[pos // 3][pos % 3] = self.turn

            self.check_for_winner(pos)
            self.turn = (self.turn + 1) % 2

            return pos

    # this is called when a message starting with "!commandname" is run
    async def execute_command(self, client, msg, content):
        pieces = [":x:", ":o:"]

        players = list(set([*msg.mentions, msg.author]))
        if len(players) != 2:
            await utils.delay_send(
                msg.channel,
                "Tic Tac Toe can only be played with 2 players, silly billy!",
            )
            return

        # make sure the tagged player is not a bot
        for player in players:
            if player is msg.author:
                continue
            if player.bot:
                await utils.delay_send(
                    msg.channel,
                    "Our code monkeys haven't trained the bots to play Tic Tac Toe yet...",
                )
                return

        players = [
            {"piece": pieces[i], "user": player} for (i, player) in enumerate(players)
        ]

        game = TicTacToe.Game(
            # note we can't use [] * 3 otherwise it creates a deep copy
            players,
            [[-1 - c - 3 * r for c in range(3)] for r in range(3)],
        )

        msg = await msg.channel.send(
            game.get_content(), embed=game.get_embed(self.get_game_footer(client))
        )

        for spot in POSITIONS[:9]:
            await msg.add_reaction(spot["emoji"])

    async def execute_reaction(self, client, reaction):
        if client.user.id == reaction.user_id:
            return

        channel = await client.fetch_channel(reaction.channel_id)
        msg = await channel.fetch_message(reaction.message_id)
        if len(msg.embeds) == 0 or msg.embeds[0].title != "Tic Tac Toe":
            return

        await msg.remove_reaction(reaction.emoji, client.get_user(reaction.user_id))

        game = TicTacToe.Game()
        game.parse_msg(msg, client)

        positions = [spot["emoji"] for spot in POSITIONS[:9]]

        if reaction.emoji.name not in positions:
            return
        if reaction.user_id != game.players[game.turn]["user"].id:
            return
        pos = game.take_turn(positions.index(reaction.emoji.name))
        if pos is None:
            return

        await msg.remove_reaction(reaction.emoji, client.user)
        await msg.edit(
            content=game.get_content(),
            embed=game.get_embed(self.get_game_footer(client)),
        )
