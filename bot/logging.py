from discord import ChannelType, File


async def log(client, msg):
    LOG_SERVER = client.get_guild(client.config["LOG_SERVER_ID"])
    if LOG_SERVER is None:
        # check does not need to be here (log_server is only necessary in the case
        # that no corresponding logging channel exists) since the client can receive
        # a channel by its id alone, but putting the check here helps ensuring a sane
        # config file
        return

    if msg.channel.type is not ChannelType.private and msg.guild != client.SERVER:
        return

    destination_channel = None
    log_content = None

    attached_files = []
    for attachment in msg.attachments:
        saved_attachment = File(f"/tmp/{msg.id}-{attachment.filename}")
        await attachment.save(saved_attachment.fp, use_cached=True)
        attached_files.append(saved_attachment)

    if msg.channel.type is ChannelType.private:
        destination_channel = LOG_SERVER.get_channel(client.config["DM_LOG_CHANNEL_ID"])
        rcvd_channel_tag = ""
        if msg.author == client.user:
            rcvd_channel_tag = (
                f" to {msg.channel.recipient.name} ({msg.channel.recipient.id})"
            )

        log_content = f"{msg.author.name} ({msg.author.id}){rcvd_channel_tag}: {msg.clean_content}"
    else:
        client.log_lock.acquire()
        client.log_c.execute(
            "SELECT dest_channel_id FROM logging WHERE source_channel_id = ?",
            str(msg.channel.id),
        )
        dest_channel_id = client.log_c.fetchone()
        client.log_lock.release()

        if dest_channel_id is None:
            destination_channel = await LOG_SERVER.create_text_channel(msg.channel.name)

            client.log_lock.acquire()
            client.log_c.execute(
                f"INSERT INTO logging (source_channel_id, dest_channel_id) VALUES ({msg.channel.id}, {destination_channel.id})"
            )
            client.log_connection.commit()
            client.log_lock.release()

        else:
            destination_channel = LOG_SERVER.get_channel(dest_channel_id[0])

        log_content = f"{msg.author.name} ({msg.author.id}): {msg.clean_content}"

    await destination_channel.send(log_content, files=attached_files)

    for attached_file in attached_files:
        os.remove(attached_file.filename)
