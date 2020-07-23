import os
from typing import cast, Iterable, List, Optional, Tuple, Union

import requests

import discord
from discord import ChannelType

from .duck import DuckClient

# action_taken gets put in front of the log message
# an example might be "(EDITED)" to show this message was edited
async def log_message(
    client: DuckClient, msg: discord.Message, action_taken: str = ""
) -> None:
    if log_server_missing(client):
        return

    if not_valid_channel(msg.channel, msg.guild, client):
        return

    try:
        destination_channel = await get_log_channel(msg.channel, client)
    except RuntimeError:
        return
    log_content = await get_log_content(msg, client)
    attached_embed = get_embed(msg)
    (attached_files_to_send, files_to_remove) = get_files(msg)

    if action_taken:
        action_taken += " "

    await destination_channel.send(
        f"{action_taken}{log_content}",
        files=attached_files_to_send,
        embed=attached_embed,
    )

    remove_files(files_to_remove)


async def log_message_delete(
    client: DuckClient, msg: discord.RawMessageDeleteEvent
) -> None:
    if msg.cached_message:
        if msg.cached_message.author.bot:
            return

        await log_message(client, msg.cached_message, "(DELETED)")
    else:
        channel_removed_from = await client.fetch_channel(msg.channel_id)
        channel_removed_from = cast(
            Union[discord.TextChannel, discord.DMChannel], channel_removed_from
        )
        destination_channel = await get_log_channel(channel_removed_from, client)
        await destination_channel.send(f"(DELETED) id:{msg.message_id}")


def not_valid_channel(
    channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
    guild: Optional[discord.Guild],
    client: DuckClient,
) -> bool:
    if channel.type is not ChannelType.private and guild != client.server:
        return True
    return False


def log_server_missing(client: DuckClient) -> bool:
    if client.log_server is None:
        # check does not need to be here (client.log_server is only necessary in the case
        # that no corresponding logging channel exists) since the client can receive
        # a channel by its id alone, but putting the check here helps ensuring a sane
        # config file
        return True
    return False


async def get_log_channel(
    channel: Union[discord.TextChannel, discord.DMChannel, discord.GroupChannel],
    client: DuckClient,
) -> discord.TextChannel:
    if channel.type is ChannelType.private and "DM_LOG_CHANNEL_ID" in client.config:
        destination_channel = client.log_server.get_channel(
            client.config["DM_LOG_CHANNEL_ID"]
        )
        destination_channel = cast(discord.TextChannel, destination_channel)
    else:
        channel = cast(discord.TextChannel, channel)
        async with client.log_lock:
            client.log_c.execute(
                "SELECT dest_channel_id FROM logging WHERE source_channel_id = :channel_id",
                {"channel_id": channel.id},
            )
            dest_channel_id = client.log_c.fetchone()

        if dest_channel_id is None:
            try:
                destination_channel = await client.log_server.create_text_channel(
                    channel.name
                )
            except discord.HTTPException:
                client.log_lock.acquire()
                client.log_c.execute("SELECT * FROM unused_logging")
                dest_channel_id = client.log_c.fetchone()[0]
                client.log_lock.release()

                destination_channel = client.log_server.get_channel(dest_channel_id[0])
                destination_channel = cast(discord.TextChannel, destination_channel)
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
            destination_channel = client.log_server.get_channel(dest_channel_id[0])
            destination_channel = cast(discord.TextChannel, destination_channel)

    return destination_channel


async def get_log_content(msg: discord.Message, client: DuckClient) -> str:
    if msg.channel.type is ChannelType.private:
        # if rubber duck is the account who sent the message
        msg.channel = cast(discord.DMChannel, msg.channel)
        rcvd_channel_tag = ""
        if msg.author == client.user:
            rcvd_channel_tag = (
                f" to {msg.channel.recipient.name} ({msg.channel.recipient.id})"
            )

        log_content = f"{msg.author.name} ({msg.author.id}){rcvd_channel_tag} [{msg.id}]: {msg.clean_content}"
    else:
        log_content = (
            f"{msg.author.name} ({msg.author.id}) [{msg.id}]: {msg.clean_content}"
        )

    return log_content


# only sends the first embed, as far as I know a message cannot have more than
# 1 embed anyway even though msg.embeds is a list
def get_embed(msg: discord.Message) -> Optional[discord.Embed]:
    attached_embed = None
    if len(msg.embeds) > 0:
        attached_embed = msg.embeds[0]
    return attached_embed


# returns the files to send and also the locations so they may be removed later
def get_files(msg: discord.Message) -> Tuple[List[discord.File], List[str]]:
    attached_file_locations = []
    for attachment in msg.attachments:
        tmp_location = f"/tmp/{msg.id}-{attachment.filename}"
        file_contents = requests.get(attachment.url, allow_redirects=True)
        open(tmp_location, "wb").write(file_contents.content)

        attached_file_locations.append(tmp_location)

    attached_files_to_send = []
    for location in attached_file_locations:
        opened_file = discord.File(location)
        attached_files_to_send.append(opened_file)
    return attached_files_to_send, attached_file_locations


def remove_files(files_to_remove: Iterable[str]) -> None:
    for location in files_to_remove:
        os.remove(location)
