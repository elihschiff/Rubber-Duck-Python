import discord

from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger
from ...logging import get_log_channel


class Merge(Command, ReactionTrigger):
    prefixes = ["%"]
    names = ["merge", "merge-with", "move"]
    description = "ADMIN ONLY: Merges a channel with another"
    usage = "!merge [channel to merge with]"
    requires_mod = True

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

        if not msg.channel_mentions or len(msg.channel_mentions) > 1:
            await utils.delay_send(msg.channel, self.usage)
            return

        merge_channel = msg.channel_mentions[0]

        async with client.log_lock:
            client.c.execute(
                "SELECT * FROM classes WHERE channel_id = :channel_id",
                {"channel_id": merge_channel.id},
            )
            if not client.c.fetchall():
                await utils.delay_send(
                    msg.channel,
                    f"ERROR: <#{merge_channel.id}> is not a class channel",
                )
                return

        await utils.delay_send(
            msg.channel,
            f"WARNING: You are about to merge this channel with <#{merge_channel.id}>.  All members of this channel will be added to <#{merge_channel.id}> and this channel will no longer be accessible. <@{author.id}> can confirm this action by reacting :+1: to this message.",
        )

    async def execute_reaction(self, client, reaction, channel, msg, user, **kwargs):
        if (
            reaction.emoji.id != client.config["thumb_id"]  # reaction must be a :+1:
            or not msg.author.bot  # must be reacting to a bot message
            or user not in msg.mentions  # prevent misclicks
            or not msg.content.startswith(
                "WARNING: You are about to merge this channel with "
            )  # we must be deleting a channel
            or not msg.channel_mentions  # we need a channel to delete
            or not any(
                react.me and react.emoji.id == client.config["thumb_id"]
                for react in msg.reactions
            )  # the bot must agree to this
        ):
            return

        await msg.clear_reactions()

        from_channel = msg.channel
        to_channel = msg.channel_mentions[0]  # only one channel per message

        # Remove this channel from the database to prevent it from being re-added
        async with client.log_lock:
            client.c.execute(
                "DELETE * FROM classes WHERE channel_id = :channel_id",
                {"channel_id": from_channel.id},
            )

        merge_msg = f"This channel has been merged with {from_channel.name}.  The following users were affected:"

        # Sync view permissions
        for member, permission in from_channel.overwrites.items():
            await to_channel.set_permissions(
                member,
                overwrite=permission,
                reason=f"Merging {from_channel.name} with {to_channel.name}",
            )

            if isinstance(member, discord.User):
                merge_msg += f" <@{member.id}>"
                # TODO: once this has been tested, the below line can be replaced with the channel deletion
                await from_channel.set_permissions(member, overwrite=None)

        merge_msg += "."

        # TODO: Delete original channel
        # await from_channel.delete(
        #     reason=f"Merging {from_channel.name} with {to_channel.name}"
        # )

        await to_channel.send(merge_msg)
