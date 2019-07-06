from . import utils
from . import NewMemberTriggers


class Welcome(NewMemberTriggers):
    async def execute(self, client, member):
        welcomeChannel = member.guild.get_channel(client.config["welcome_channel_id"])
        if welcomeChannel:
            await welcomeChannel.send(client.messages["welcome"].format(member.mention))

    # TODO this only sends the public part, the dm still needs to be added
