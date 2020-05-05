from .new_member_trigger import NewMemberTrigger


class Welcome(NewMemberTrigger):
    async def execute_new_member(self, client, member):
        welcome_channel = client.get_channel(client.config["welcome_channel_id"])
        if welcome_channel:
            await welcome_channel.send(
                client.messages["welcome_public"].format(member.mention)
            )

        if client.config["ENABLE_COURSES"]:
            non_all_seer = client.server.get_role(client.config["non_all_seer_id"])
            await member.add_roles(non_all_seer)

            await member.send(client.messages["welcome_dm"])
