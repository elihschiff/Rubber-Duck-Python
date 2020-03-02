from .games import Game, GLOBAL_GAMES
from ..reaction_trigger import ReactionTrigger

import discord
import re

reaccs = [
    {"emoji": "\U0001f311", "name": ":new_moon:"},
    {"emoji": "\U0001f4f0", "name": ":newspaper:"},
    {"emoji": "\u2702", "name": ":scissors:"},
]


class RPSGame:
    def __init__(self, orig_msg, players, message_ids):
        # initialize answers
        self.orig_channel = orig_msg.channel.id
        self.msg_ids = message_ids
        self.players = players
        self.answer_dict = dict()
        for player in players:
            self.answer_dict[player] = ""

    def check_winner(self):
        answers = [self.answer_dict[player] for player in self.players]
        # somebody didn't answer yet >:(
        if answers[0] == "" or answers[1] == "":
            return False

        for i in range(len(answers)):
            if answers[i] == reaccs[0]["emoji"]:
                # rock
                answers[i] = 0
            elif answers[i] == reaccs[1]["emoji"]:
                # paper
                answers[i] = 1
            elif answers[i] == reaccs[2]["emoji"]:
                # scissors
                answers[i] = 2

        result = answers[0] - answers[1]
        # result == 0 iff they are the same
        if result == 0:
            return 0
        elif result == 1 or result == -2:
            return 1
        elif result == -1 or result == 2:
            return 2

        print("RPS: We shouldn't get here!")
        return False


class RockPaperScissors(Game, ReactionTrigger):
    names = ["rps", "rockpaperscissors"]
    description = "Begins a game of Rock Paper Scissors with a player."
    usage = "!rps [@ another user]"

    def get_content(self):
        return "You have been challenged to RPS!"

    def get_pm_embed(self, players, client):
        embed = discord.Embed(
            title="Rock Paper Scissors", description="Please react your move!"
        )

        embed.add_field(
            name="Players", value=" vs. ".join([player.mention for player in players])
        )

        embed.set_footer(text=self.get_game_footer(client))
        return embed

    def get_wait_embed(self, waiting_for, players, client):

        embed = discord.Embed(
            title="Rock Paper Scissors",
            description=f"Nice pick!\nWaiting for {waiting_for}",
        )

        embed.set_footer(text=self.get_game_footer(client))
        return embed

    # this is called when a message starting with "!commandname" is run
    async def execute_command(self, client, msg, content):
        if not content:
            await utils.delay_send(msg.channel, f"Usage: {self.usage}")
            return

        pieces = [":new_moon:", ":newspaper:", ":scissors:"]

        players = list(set([*msg.mentions, msg.author]))
        if len(players) != 2:
            await msg.channel.send(client.messages["rockpaperscissors_num_players"])
            return

        # make sure the tagged player is not a bot
        for player in players:
            if player.bot:
                await msg.channel.send(client.messages["rockpaperscissors_bot_player"])
                return

        # collect the players to hash for game management
        player_set = frozenset([player.mention for player in players])

        # verify that the key is in the game dictionary
        if player_set not in GLOBAL_GAMES.keys():
            GLOBAL_GAMES[player_set] = []

        # ensure there is no pre-existing RPS game
        games = GLOBAL_GAMES[player_set]
        for game in games:
            if isinstance(game, RPSGame):
                print("Error: There is already an active RPS game between", player_set)
                await msg.channel.send(
                    client.messages["rockpaperscissors_existing_game"].format(
                        players[0].mention, players[1].mention
                    )
                )
                return

        msg_ids = []

        # send players RPS messages
        for player in players:
            tmp = await player.send(
                content=self.get_content(), embed=self.get_pm_embed(players, client)
            )
            for spot in reaccs:
                await tmp.add_reaction(spot["emoji"])
            msg_ids.append(tmp.id)

        # initialize the game in the game manager
        games.append(RPSGame(msg, [player.id for player in players], msg_ids))

        msg.channel.send(client.messages["rockpaperscissors_game_init"])

    async def execute_reaction(self, client, reaction, channel, msg, user):
        if client.user.id == reaction.user_id:
            return

        # channel = await client.fetch_channel(reaction.channel_id)
        # msg = await channel.fetch_message(reaction.message_id)

        if len(msg.embeds) == 0 or msg.embeds[0].title != "Rock Paper Scissors":
            return

        options = [spot["emoji"] for spot in reaccs]

        if reaction.emoji.name not in options:
            return

        # grab the players
        players = []
        for field in msg.embeds[0].fields:
            if field.name == "Players":
                players = field.value.split(" vs. ")
                break

        # find the game in the global game dict
        if frozenset(players) not in GLOBAL_GAMES.keys():
            await channel.send(content="Sorry, this RPS game is out of date!")
            return
        games = GLOBAL_GAMES[frozenset(players)]
        this_game = None

        for game in games:
            if isinstance(game, RPSGame):
                this_game = game
                break
        if this_game is None:
            print("Couldn't find RPS game between", players[0], "and", players[1])
            return

        # store the answer (in Unicode form)
        if game.answer_dict[reaction.user_id] != "":
            return
        game.answer_dict[reaction.user_id] = reaction.emoji.name

        # check if there is a winner
        result = game.check_winner()
        if result is not False:
            player1, player2 = players
            answer1, answer2 = [ans for ans in game.answer_dict.values()]

            content = f"{player1} and {player2}:\nThe results are in!\n"

            embed = discord.Embed(
                title="Rock Paper Scissors",
                description=f"{player1}: {answer1}\n{player2}: {answer2}\n\n",
            )

            embed.set_footer(text=self.get_game_footer(client))

            if result == 0:
                embed.add_field(name="Result", value="Draw!")
            elif result == 1:
                embed.add_field(name="Result", value=f"{player1} wins!")
            elif result == 2:
                embed.add_field(name="Result", value=f"{player2} wins!")

            # grab the original channel and send who won
            orig_channel = await client.fetch_channel(game.orig_channel)
            notif = await orig_channel.send(content=content, embed=embed)

            # edit the private messages and shortly after, delete them
            for user_id, message_id in zip(game.players, game.msg_ids):
                usr = await client.fetch_user(user_id)
                dm_channel = usr.dm_channel
                dm = await dm_channel.fetch_message(message_id)
                await dm.delete()

            # delete the game so people can play again
            GLOBAL_GAMES[frozenset(players)].remove(game)
            return False
        else:
            # still waiting so tell the player that they're waiting

            author = await client.fetch_user(reaction.user_id)
            waiting_for = None

            for player in players:
                player_id = re.search("<@!?(\d+)>", player)
                if int(player_id.group(1)) != author.id:
                    waiting_for = player
                    break
            if waiting_for is None:
                print("ERROR\tRPS: can't find opponent!")
                return

            await msg.edit(
                content="", embed=self.get_wait_embed(waiting_for, players, client)
            )
