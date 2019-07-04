from .. import MessageTrigger


class Command(MessageTrigger):
    prefixes = ["!"]

    def is_valid(self, msg) -> int:
        if msg.author.bot:
            return None

        command = ""
        for name in self.names:
            for prefix in self.prefixes:
                if msg.content.startswith(f"{prefix}{name}"):
                    command = prefix+name;
                    break
            if command:
                break

        if not command:
            return None
        try:
            if self.is_valid_command(msg):
                return len(command)
        except:
            return len(command)

    async def execute(self, client, msg) -> bool:
        idx = self.is_valid(msg)
        if idx is None:
            return False

        await self.execute_command(client, msg, msg.content[idx + 1 :])
        return True

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")


from .echo import Echo
from .ai import AI

# Please keep in alphabetical order
all_commands = [AI(), Echo()]
