import discord
from discord import ChannelType
import requests
import os

# action_taken gets put in front of the log message
# an example might be "(EDITED)" to show this message was edited
async def log_message(client, msg, action_taken=""):
    if log_server_missing(client):
        return

    if not_valid_channel(msg.channel, msg.guild, client):
        return

    destination_channel = await get_log_channel(msg.channel, client)
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


async def log_message_delete(client, msg):
    if msg.cached_message:
        if msg.author.bot:
            return

        await log_message(client, msg.cached_message, "(DELETED)")
    else:
        channel_removed_from = await client.fetch_channel(msg.channel_id)
        destination_channel = await get_log_channel(channel_removed_from, client)
        await destination_channel.send(f"(DELETED) id:{msg.message_id}")


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
        client.log_lock.acquire()
        client.log_c.execute(
            f"SELECT dest_channel_id FROM logging WHERE source_channel_id = {channel.id}"
        )
        dest_channel_id = client.log_c.fetchone()
        client.log_lock.release()

        if dest_channel_id is None:
            destination_channel = await client.LOG_SERVER.create_text_channel(
                channel.name
            )

            client.log_lock.acquire()
            client.log_c.execute(
                f"INSERT INTO logging (source_channel_id, dest_channel_id) VALUES ({channel.id}, {destination_channel.id})"
            )
            client.log_connection.commit()
            client.log_lock.release()

        else:
            destination_channel = client.LOG_SERVER.get_channel(dest_channel_id[0])

    return destination_channel


async def get_log_content(msg, client):
    if msg.channel.type is ChannelType.private:
        # if rubber duck is the account who sent the message
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
def get_embed(msg):
    attached_embed = None
    if len(msg.embeds) > 0:
        attached_embed = msg.embeds[0]
    return attached_embed


# returns the files to send and also the locations so they may be removed later
def get_files(msg):
    attached_file_locations = []
    for attachment in msg.attachments:
        tmp_location = f"/tmp/{msg.id}-{attachment.filename}"
        r = requests.get(attachment.url, allow_redirects=True)
        open(tmp_location, "wb").write(r.content)

        attached_file_locations.append(tmp_location)

    attached_files_to_send = []
    for location in attached_file_locations:
        opened_file = discord.File(location)
        attached_files_to_send.append(opened_file)
    return attached_files_to_send, attached_file_locations


def remove_files(files_to_remove):
    for location in files_to_remove:
        os.remove(location)
