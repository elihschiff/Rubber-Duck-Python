from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger

import discord
import random

COLUMNS = [
    *[str(i) + "\u20E3" for i in range(10)],
    "\U0001F51F",
    *[chr(0x1F1E6 + i) for i in range(9)],
]


class ConnectFourGame:
    def __init__(self, pieces, players, rows, cols):
        self.pieces = pieces

        self.players = players
        self.turn = 0

        self.cols = COLUMNS[:cols]
        self.board = [[-1] * cols for i in range(rows)]

        self.message = None
        self.winner = None

    def columns(self):
        return "".join(
            [
                col
                + ("\u200B" if col >= chr(0x1F1E6) and col <= chr(0x1F1E6 + 9) else "")
                for col in self.cols
            ]
        )

    def content(self):
        if self.get_winner() is not None:
            return f"{self.players[self.get_winner()].mention} has won!"
        else:
            return f"It's {self.players[self.turn].mention}'s turn."

    def embed(self):
        title = " vs. ".join(
            [
                self.pieces[i] + " " + player.name
                for i, player in enumerate(self.players)
            ]
        )
        desc = (
            self.columns()
            + "\n"
            + "\n".join(
                [
                    "".join(
                        [
                            self.pieces[piece] if piece != -1 else "\u26AB"
                            for piece in row
                        ]
                    )
                    for row in self.board
                ]
            )
            + "\n"
            + self.columns()
        )

        embed = discord.Embed(title=title, description=desc)
        embed.set_author(name="Connect Four")
        embed.set_footer(text="Duck Games by @Elly")

        return embed

    def can_send(self):
        embed = self.embed()
        # TODO: actual desc length seems to be longer than embed.description length
        #       since unicode characters are expanded into emoji sequences
        return len(embed) <= 6000 and len(embed.description) < 2048

    async def start(self, channel):
        self.message = await utils.delay_send(
            channel, self.content(), embed=self.embed()
        )
        for col in self.cols:
            await self.message.add_reaction(col)

    async def update(self):
        if self.message is None:
            return
        await self.message.edit(content=self.content(), embed=self.embed())

    def get_line(self, row, col, row_step, col_step, length):
        player = self.board[row][col]
        if player == -1:
            return None

        # iterate down the line
        for piece in range(length - 1):
            row += row_step
            col += col_step
            # return None if the position is off the board or the line is incomplete
            if row < 0 or col < 0 or row >= len(self.board) or col >= len(self.cols):
                return None
            if self.board[row][col] != player:
                return None
        return player

    def get_winner(self):
        # use cached winner to prevent repetitive board lookup
        if self.winner is not None:
            return self.winner

        # iterate through every position on the board
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                # lookup lines in positive directions (down and/or right)
                for row_step in range(2):
                    for col_step in range(2):
                        if row_step == 0 and col_step == 0:
                            continue
                        winner = self.get_line(row, col, row_step, col_step, 4)
                        if winner is not None:
                            self.winner = winner
                            return winner
        return None


class ConnectFour(Command, ReactionTrigger):
    names = ["c4", "connect4", "connectfour"]
    description = "Begins a Connect Four game with another player(s)"
    needsContent = True

    games = []

    async def execute_command(self, client, msg, content):
        if len(self.games) >= client.config["connectfour"]["max_games"]:
            await msg.channel.send(client.messages["connectfour_err_games"])
            return

        pieces = (
            client.config["connectfour"]["pieces"]
            if "pieces" in client.config["connectfour"]
            else ["\U0001F534", "\U0001F535", "\u26AA"]
        )

        players = list(set([*msg.mentions, msg.author]))
        if len(players) < 2:
            await utils.delay_send(
                msg.channel, client.messages["connectfour_err_no_opponent"]
            )
            return
        max_players = min(client.config["connectfour"]["max_players"], len(pieces))
        if len(players) > max_players:
            await msg.channel.send(client.messages["connectfour_err_players"])
            return
        random.shuffle(players)

        rows = utils.get_flag("r", content, "6")
        if not rows.isdigit():
            await msg.channel.send(client.messages["connectfour_err_num"])
            return
        rows = int(rows)
        if rows < 4:
            await msg.channel.send(client.messages["connectfour_err_min_rows"])
            return
        max_rows = client.config["connectfour"]["max_rows"]
        if rows > max_rows:
            await msg.channel.send(
                client.messages["connectfour_err_max_rows"].format(max_rows)
            )
            return

        cols = utils.get_flag("c", content, "7")
        if not cols.isdigit():
            await msg.channel.send(client.messages["connectfour_err_num"])
            return
        cols = int(cols)
        if cols < 4:
            await msg.channel.send(client.messages["connectfour_err_min_cols"])
            return
        max_cols = min(client.config["connectfour"]["max_cols"], len(COLUMNS))
        if cols > max_cols:
            await msg.channel.send(
                client.messages["connectfour_err_max_cols"].format(max_cols)
            )
            return

        game = ConnectFourGame(pieces, players, rows, cols)
        if not game.can_send():
            await msg.channel.send(client.messages["connectfour_err_size"])
            return
        await game.start(msg.channel)
        self.games.append(game)

    async def execute_reaction(self, client, reaction):
        if client.user.id == reaction.user_id:
            return
        for game in self.games:
            if game.message is None:
                continue
            if game.message.id != reaction.message_id:
                continue

            channel = await client.fetch_channel(reaction.channel_id)
            message = await channel.fetch_message(reaction.message_id)
            await message.remove_reaction(
                reaction.emoji, client.get_user(reaction.user_id)
            )

            if game.players[game.turn].id != reaction.user_id:
                continue
            if reaction.emoji.name not in game.cols:
                continue

            col = game.cols.index(reaction.emoji.name)
            # ignore if the top row of this column is occupied
            if game.board[0][col] != -1:
                continue
            row = 0
            while row + 1 < len(game.board) and game.board[row + 1][col] == -1:
                row += 1
            game.board[row][col] = game.turn
            if row == 0:
                await message.remove_reaction(reaction.emoji, client.user)

            game.turn = (game.turn + 1) % len(game.players)

            await game.update()
            if game.get_winner() is not None:
                self.games.remove(game)
