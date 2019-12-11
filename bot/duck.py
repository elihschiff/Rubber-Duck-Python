import discord


class DuckClient(discord.Client):
    async def on_ready(self):
        print(f"Connected as {self.user}!")
