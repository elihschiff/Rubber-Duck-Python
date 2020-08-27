import discord
from discord import ChannelType
import os
from .triggers.utils import get_aiohttp
from io import BytesIO

# action_taken gets put in front of the log message
# an example might be "(EDITED)" to show this message was edited
async def log_message(client, msg, action_taken=""):
    if log_server_missing(client):
        return

    if not_valid_channel(msg.channel, msg.guild, client):
        return

    if msg.channel.type is ChannelType.private:
        destination_channel = client.LOG_SERVER.get_channel(
            client.config["DM_LOG_CHANNEL_ID"]
        )
    else:
        destination_channel = client.LOG_SERVER.get_channel(
            client.config["LOG_CHANNEL_ID"]
        )
    log_content = await get_log_content(msg, client)
    attached_embed = get_embed(msg)

    if action_taken:
        action_taken += " "

    files = [await attach.to_file() for attach in msg.attachments]

    await destination_channel.send(
        f"{action_taken}{log_content}",
        files=files,
        embed=attached_embed,
    )


async def log_message_delete(client, msg):
    if msg.cached_message:
        if msg.cached_message.author.bot:
            return

        await log_message(client, msg.cached_message, "(DELETED)")
    else:
        channel_removed_from = await client.fetch_channel(msg.channel_id)
        if channel_removed_from.type is ChannelType.private:
            destination_channel = client.LOG_SERVER.get_channel(
                client.config["DM_LOG_CHANNEL_ID"]
            )
        else:
            destination_channel = client.LOG_SERVER.get_channel(
                client.config["LOG_CHANNEL_ID"]
            )
        await destination_channel.send(
            f"({channel_removed_from.id}) - (DELETED) id:{msg.message_id}"
        )


def not_valid_channel(channel, guild, client):
    if channel.type is not ChannelType.private and guild != client.SERVER:
        return True
    return False


def log_server_missing(client):
    if client.LOG_SERVER is None:
        # check does not need to be here (client.LOG_SERVER is only necessary in the case
        # that no corresponding logging channel exists) since the client can receive
        # a channel by its id alone, but putting the check here helps ensuring a sane
        # config file
        return True
    return False


async def get_log_channel(channel, client):
    if channel.type is ChannelType.private:
        destination_channel = client.LOG_SERVER.get_channel(
            client.config["DM_LOG_CHANNEL_ID"]
        )
    else:
        async with client.log_lock:
            client.log_c.execute(
                "SELECT dest_channel_id FROM logging WHERE source_channel_id = :channel_id",
                {"channel_id": channel.id},
            )
            dest_channel_id = client.log_c.fetchone()

        if dest_channel_id is None:
            try:
                destination_channel = await client.LOG_SERVER.create_text_channel(
                    channel.name
                )
            except discord.HTTPException:
                client.log_lock.acquire()
                client.log_c.execute("SELECT * FROM unused_logging")
                dest_channel_id = client.log_c.fetchone()[0]
                client.log_lock.release()

                destination_channel = client.LOG_SERVER.get_channel(dest_channel_id[0])
                await destination_channel.edit(name=channel.name)
                await destination_channel.send(f"CHANNEL NOW LOGGING: {channel.name}")

            async with client.log_lock:
                client.log_c.execute(
                    "INSERT INTO logging (source_channel_id, dest_channel_id) VALUES (:channel_id, :destination_channel_id)",
                    {
                        "channel_id": channel.id,
                        "destination_channel_id": destination_channel.id,
                    },
                )
                client.log_connection.commit()

        else:
            destination_channel = client.LOG_SERVER.get_channel(dest_channel_id[0])

    return destination_channel


async def get_log_content(msg, client):
    if msg.channel.type is ChannelType.private:
        # if rubber duck is the account who sent the message
        rcvd_channel_tag = ""
        if msg.author == client.user:
            rcvd_channel_tag = (
                f" to @{msg.channel.recipient.name} ({msg.channel.recipient.id})"
            )

        log_content = f"@{msg.author.name} ({msg.author.id}){rcvd_channel_tag} [{msg.id}]: {msg.clean_content}"
    else:
        log_content = f"#{msg.channel.name} ({msg.channel.id}) - @{msg.author.name} ({msg.author.id}) [{msg.id}]: {msg.clean_content}"

    return log_content


# only sends the first embed, as far as I know a message cannot have more than
# 1 embed anyway even though msg.embeds is a list
def get_embed(msg):
    attached_embed = None
    if len(msg.embeds) > 0:
        attached_embed = msg.embeds[0]
    return attached_embed
