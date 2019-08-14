from discord import ChannelType, File
import json


async def log(client, msg):
    LOG_SERVER = client.get_guild(client.logging["LOG_SERVER_ID"])
    if LOG_SERVER is None:
        # check does not need to be here (log_server is only necessary in the case
        # that no corresponding logging channel exists) since the client can receive
        # a channel by its id alone, but putting the check here helps ensuring a sane
        # config file
        return

    if msg.channel.type is not ChannelType.private and msg.guild != client.SERVER:
        return

    json_dirty = False

    destination_channel = None
    log_content = None

    attached_files = []
    for attachment in msg.attachments:
        saved_attachment = File(f"/tmp/{msg.id}-{attachment.filename}")
        await attachment.save(saved_attachment.fp, use_cached=True)
        attached_files.append(saved_attachment)

    if msg.channel.type is ChannelType.private:
        destination_channel = LOG_SERVER.get_channel(client.logging["DM_LOGS"])
        rcvd_channel_tag = ""
        if msg.author == client.user:
            rcvd_channel_tag = (
                f" to {msg.channel.recipient.name} ({msg.channel.recipient.id})"
            )

        log_content = f"{msg.author.name} ({msg.author.id}){rcvd_channel_tag}: {msg.clean_content}"
    else:
        if msg.channel.id not in client.logging:
            source_category = msg.channel.category
            destination_category = None
            if source_category.id not in client.logging:
                destination_category = await LOG_SERVER.create_category_channel(
                    source_category.name
                )
                client.logging[f"{source_category.id}"] = destination_category.id
            else:
                destination_category = LOG_SERVER.get_channel(
                    client.logging(f"{source_category.id}")
                )

            destination_channel = await LOG_SERVER.create_text_channel(
                msg.channel.name, category=destination_category
            )
            client.logging[f"{msg.channel.id}"] = destination_channel.id

            json_dirty = True
        else:
            destination_channel = LOG_SERVER.get_channel(
                client.logging[f"{msg.channel.id}"]
            )

        log_content = f"{msg.author.name} ({msg.author.id}): {msg.clean_content}"

    await destination_channel.send(log_content, files=attached_files)

    for attached_file in attached_files:
        os.remove(attached_file.filename)

    if json_dirty:
        with open(client.logging_filename, "w") as logging_file:
            json.dump(client.logging, logging_file)
