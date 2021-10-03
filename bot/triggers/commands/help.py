from . import Command, all_commands
from .. import utils
import nextcord


class Help(Command):
    names = ["help"]
    description = "Lists commands and their description"
    show_in_help = True

    async def execute_command(self, client, msg, content, **kwargs):
        args = content.split(" ")
        # if a specific command for help was entered
        if args[0].strip() != "":
            for command in all_commands:
                for name in utils.get_correct_attr(command, "names", client):
                    if name == args[0]:
                        names = utils.get_correct_attr(command, "names", client)
                        desc = utils.get_correct_attr(command, "description", client)
                        usage = utils.get_correct_attr(command, "usage", client)
                        examples = utils.get_correct_attr(command, "examples", client)
                        notes = utils.get_correct_attr(command, "notes", client)

                        embed_title = f"{names[0]} command:"
                        command_help = ""
                        if desc:
                            command_help += f"\n**Description**: {desc}"
                        if usage:
                            command_help += f"\n**Usage**: {usage}"
                        if examples:
                            command_help += f"\n**Examples**: {examples}"
                        if len(names) > 1:
                            alt_name_str = ", ".join(
                                [f"{command.prefixes[0]}{name}" for name in names[1:]]
                            )
                            command_help += f"\n**Alternative names**: {alt_name_str}"
                        if notes:
                            command_help += f"\n**Notes**: {notes}"

                        response = nextcord.Embed(
                            title=embed_title, description=command_help
                        )
                        await send_embed(msg, response, embed_title)
                        return
            await utils.delay_send(
                msg.channel, f"Could not find command `{args[0]}`.\n", reply_to=msg
            )
            return

        # otherwise, list all commands and their descriptions
        await utils.delay_send(
            msg.author,
            'Here are all general commands. To get help for a specific command,\
 write "!help [command name]" (ex: !help add).\n',
        )

        commands_arr = []
        for command in all_commands:
            command_names = utils.get_correct_attr(command, "names", client)
            command_desc = utils.get_correct_attr(command, "description", client)
            if utils.get_correct_attr(command, "show_in_help", client):
                if command.description:
                    commands_arr.append(
                        f"**{command.prefixes[0]}{command_names[0]}:** {command_desc}\n"
                    )

        max_char_count = 2000
        commands_str = ""
        title = "General Commands"
        for line in commands_arr:
            if len(commands_str) + len(line) < max_char_count:
                commands_str += line
            else:
                response = nextcord.Embed(title=title, description=commands_str)
                await send_embed(msg, response, title)
                commands_str = line
                title = ""

        response = nextcord.Embed(title=title, description=commands_str)
        await send_embed(msg, response, title)

        if msg.channel.type is not nextcord.ChannelType.private:
            await utils.delay_send(msg.channel, "DMed!", reply_to=msg)


async def send_embed(msg, embed, title):
    # only delay send if it's the first message
    if title:
        await utils.delay_send(msg.author, "", embed=embed)
    else:
        await msg.author.send("", embed=embed)
