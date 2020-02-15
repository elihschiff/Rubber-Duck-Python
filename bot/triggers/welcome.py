from . import utils
from .new_member_trigger import NewMemberTrigger


class Welcome(NewMemberTrigger):
    async def execute_new_member(self, client, member):
        welcomeChannel = client.get_channel(client.config["welcome_channel_id"])
        if welcomeChannel:
            await welcomeChannel.send(
                client.messages["welcome_public"].format(member.mention)
            )
