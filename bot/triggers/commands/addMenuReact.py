from .. import utils
from .. import ReactionTrigger


class AddMenuReact(ReactionTrigger):
    async def execute(self, client, reaction, usr):
        # todo check if user is the same as the person who was tagged in react
        # we may not actually want to add this it was in the js but I dont remmber
        # why it was there in the first place

        if usr.bot:
            return

        # print(str(reaction))
        emojiNumbers = [
            "\u0030\u20E3",
            "\u0031\u20E3",
            "\u0032\u20E3",
            "\u0033\u20E3",
            "\u0034\u20E3",
            "\u0035\u20E3",
            "\u0036\u20E3",
            "\u0037\u20E3",
            "\u0038\u20E3",
            "\u0039\u20E3",
        ]
        noMatchingResultsEmote = "🚫"

        react_str = str(reaction)

        if react_str == noMatchingResultsEmote:
            # todo the js has it send a new message, but we might want to make
            # this work as an edit instead
            await reaction.message.channel.send(
                "Sorry it looks like I could not find the class you are looking for in my databse. Feel free to contact the mods to have it added."
            )
            return

        if react_str not in emojiNumbers:
            return

        # print(reaction.message.content)
        lines = reaction.message.content.split("\n")
        for line in lines:
            if line.startswith(react_str):
                class_name = line.replace(react_str, "").strip().split("\t")[0]
                roles = reaction.message.guild.roles
                # print(roles)
                for role in roles:
                    # print(role.name)
                    if role.name == class_name:
                        print(class_name)
                        await usr.add_roles(role)
                        return

                # role must not exist so channel does not exist as well
