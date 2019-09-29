import discord
from discord import ChannelType
import requests
import os


async def log(client, msg):
    if client.LOG_SERVER is None:
        # check does not need to be here (client.LOG_SERVER is only necessary in the case
        # that no corresponding logging channel exists) since the client can receive
        # a channel by its id alone, but putting the check here helps ensuring a sane
        # config file
        return

    if msg.channel.type is not ChannelType.private and msg.guild != client.SERVER:
        return

    destination_channel = None
    log_content = None

    attached_file_locations = []
    for attachment in msg.attachments:
        tmp_location = f"/tmp/{msg.id}-{attachment.filename}"
        r = requests.get(attachment.url, allow_redirects=True)
        open(tmp_location, "wb").write(r.content)

        attached_file_locations.append(tmp_location)

    if msg.channel.type is ChannelType.private:
        destination_channel = client.LOG_SERVER.get_channel(
            client.config["DM_LOG_CHANNEL_ID"]
        )
        rcvd_channel_tag = ""
        if msg.author == client.user:
            rcvd_channel_tag = (
                f" to {msg.channel.recipient.name} ({msg.channel.recipient.id})"
            )

        log_content = f"{msg.author.name} ({msg.author.id}){rcvd_channel_tag}: {msg.clean_content}"
    else:
        client.log_lock.acquire()
        client.log_c.execute(
            f"SELECT dest_channel_id FROM logging WHERE source_channel_id = {msg.channel.id}"
        )
        dest_channel_id = client.log_c.fetchone()
        client.log_lock.release()

        if dest_channel_id is None:
            destination_channel = await client.LOG_SERVER.create_text_channel(
                msg.channel.name
            )

            client.log_lock.acquire()
            client.log_c.execute(
                f"INSERT INTO logging (source_channel_id, dest_channel_id) VALUES ({msg.channel.id}, {destination_channel.id})"
            )
            client.log_connection.commit()
            client.log_lock.release()

        else:
            destination_channel = client.LOG_SERVER.get_channel(dest_channel_id[0])

        log_content = f"{msg.author.name} ({msg.author.id}): {msg.clean_content}"

    # only sends the first embed, as far as I know a message cannot have more than
    # 1 embed anyway even though msg.embeds is a list
    attached_embed = None
    if len(msg.embeds) > 0:
        attached_embed = msg.embeds[0]

    attached_files_to_send = []
    for location in attached_file_locations:
        opened_file = discord.File(location)
        attached_files_to_send.append(opened_file)

    await destination_channel.send(
        log_content, files=attached_files_to_send, embed=attached_embed
    )

    for location in attached_file_locations:
        os.remove(location)
