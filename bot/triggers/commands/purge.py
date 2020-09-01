from datetime import timedelta, datetime

from . import Command
from .. import utils
from ..reaction_trigger import ReactionTrigger
from ...logging import get_log_channel

ONE_MONTH = timedelta(weeks=4)

# Motivation: At the start of a new semester, it's hard to delete all inactive channels,
# and this must be done in a time-crunch as students are rapidly adding classes.
#
# This command automates the selection of deletion candidates while keeping the decision
# for which channels to actually delete in the hands of a human.
class Purge(Command):
    prefixes = ["%"]
    names = ["purge", "sudo rm -rf ."]
    description = "ADMIN ONLY: Prompts for deletion of all inactive channels"
    requires_mod = True

    # Copied directly from bot/triggers/commands/delete.py to ensure compatibility.
    # This will have to be updated if the delete syntax ever changes.
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

    # Returns a list of reasons to delete the channel, if there are any
    # The reasons are just strings for simplicity
    async def get_deletion_reasons(self, client, channel):
        reasons = []

        async with client.log_lock:
            client.c.execute(
                "SELECT * FROM classes WHERE channel_id = :channel_id",
                {"channel_id": channel.id},
            )
            chan = client.c.fetchone()
            if not chan:
                # just ignore the error (as if this isn't a valid channel to purge)
                return []
            else:
                active = chan[6]
                if active == 0:
                    reasons.append("This course is not currently offered")

        current_date = datetime.today()

        """
        # Current commented out since a lot of channels don't get much activity

        ONE_MONTH_AGO = current_date - ONE_MONTH

        message_sent_in_last_month = False
        async for message in channel.history(after=ONE_MONTH_AGO):
            if message.author != client.user:
                message_sent_in_last_month = True
                break

        if not message_sent_in_last_month:
            reasons.append("The last message was sent over a month ago")
        """

        SPRING_JOIN_START = datetime(current_date.year - 1, 8, 15)
        SUMMER_JOIN_START = datetime(current_date.year, 3, 15)
        FALL_JOIN_START = datetime(current_date.year, 4, 1)

        if current_date > FALL_JOIN_START:
            CURR_SEMESTER_START = FALL_JOIN_START
        elif current_date > SUMMER_JOIN_START:
            CURR_SEMESTER_START = SUMMER_JOIN_START
        else:
            CURR_SEMESTER_START = SPRING_JOIN_START

        bot_message_sent_in_semester = False

        async for message in channel.history(after=CURR_SEMESTER_START):
            if message.author == client.user:
                bot_message_sent_in_semester = True
                break

        if not bot_message_sent_in_semester:
            reasons.append(
                "No one has added the course since registration for this semester opened"
            )

        return reasons

    async def send_deletion_reasons(self, client, channel, reasons):
        message = "Reason(s) for deletion:\n"
        for reason in reasons:
            message += f"- {reason}\n"
        await channel.send(message)
        await channel.send(
            "This deletion prompt was automatically generated.  A moderator will confirm that this channel should be deleted before deleting it."
        )

    async def execute_command(self, client, msg, content):
        if not client.config["ENABLE_COURSES"]:
            await utils.delay_send(
                msg.channel,
                "ERROR: I have been configured to not support courses.  Aborting...",
            )
            return

        if not msg.author.guild_permissions.administrator:
            utils.delay_send(msg.channel, client.messages["invalid_permissions"])
            return

        await msg.channel.send(
            "Checking for which channels are potentially eligible to be deleted.  THIS IS NOT A PERFECT PROCESS, make sure to check that the channels actually should be deleted."
        )

        for category_channel_id in client.config["class_category_ids"]:
            category_channel = client.get_channel(category_channel_id)
            for course_channel in category_channel.text_channels:
                deletion_reasons = await self.get_deletion_reasons(
                    client, course_channel
                )
                if not deletion_reasons:
                    continue

                print(f"Will delete {course_channel.name}")

                await self.prompt_for_channel_deletion(
                    client, course_channel, course_channel, msg.author
                )
                await self.send_deletion_reasons(
                    client, course_channel, deletion_reasons
                )
