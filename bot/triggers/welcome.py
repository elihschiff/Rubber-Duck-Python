from . import utils
from . import NewMemberTrigger


class Welcome(NewMemberTrigger):
    async def execute(self, client, member):
        welcomeChannel = client.get_channel(client.config["welcome_channel_id"])
        if welcomeChannel:
            await welcomeChannel.send(
                client.messages["welcome_public"].format(member.mention)
            )

        await member.send(client.messages["welcome_dm"])
