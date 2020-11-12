from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger
from ...logging import get_log_channel


class Delete(Command, ReactionTrigger):
    prefixes = ["%"]
    names = ["delete", "sude rm -f ."]
    description = "ADMIN ONLY: Deletes a channel"
    requires_mod = True

    async def prompt_for_channel_deletion(
        self, client, command_channel, channel_to_delete, author
    ):
        async with client.log_lock:
            client.c.execute(
                "SELECT * FROM classes WHERE channel_id = :channel_id",
                {"channel_id": channel_to_delete.id},
            )
            if not client.c.fetchall():
                await utils.delay_send(
                    command_channel,
                    f"ERROR: <#{channel_to_delete.id}> is not a class channel",
                )
                return

        msg = await utils.delay_send(
            command_channel,
            f"WARNING: You are about to delete <#{channel_to_delete.id}>.  <@{author.id}> can confirm this action by reacting :+1: to this message.",
        )
        await msg.add_reaction(client.get_emoji(client.config["thumb_id"]))

    async def execute_command(self, client, msg, content, **kwargs):
        if not client.config["ENABLE_COURSES"]:
            await utils.delay_send(
                msg.channel,
                "ERROR: I have been configured to not support courses.  Aborting...",
            )
            return

        if not msg.author.guild_permissions.administrator:
            utils.delay_send(msg.channel, client.messages["invalid_permissions"])
            return

        if not msg.channel_mentions:
            await self.prompt_for_channel_deletion(
                client,
                msg.channel,
                msg.channel,
                msg.author,
            )
            return

        for channel in msg.channel_mentions:
            await self.prompt_for_channel_deletion(
                client,
                msg.channel,
                channel,
                msg.author,
            )

    async def execute_reaction(self, client, reaction, channel, msg, user, **kwargs):
        if (
            reaction.emoji.id != client.config["thumb_id"]  # reaction must be a :+1:
            or not msg.author.bot  # must be reacting to a bot message
            or user not in msg.mentions  # prevent misclicks
            or not msg.content.startswith(
                "WARNING: You are about to delete "
            )  # we must be deleting a channel
            or not msg.channel_mentions  # we need a channel to delete
            or not any(
                react.me and react.emoji.id == client.config["thumb_id"]
                for react in msg.reactions
            )  # the bot must agree to this
        ):
            return

        await msg.clear_reactions()

        channel_to_delete = msg.channel_mentions[0]  # only one channel per message
        deleted_id = channel_to_delete.id

        async with client.lock:
            await channel_to_delete.delete()

            client.c.execute(
                "UPDATE classes SET channel_id = 0 WHERE channel_id = :channel_id;",
                {"channel_id": deleted_id},
            )
            client.connection.commit()
