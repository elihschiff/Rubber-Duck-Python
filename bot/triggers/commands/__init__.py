from .. import MessageTrigger
import re


class Command(MessageTrigger):
    prefixes = ["!"]

    def is_valid(self, msg) -> int:
        if msg.author.bot:
            return None

        command = ""
        for name in self.names:
            for prefix in self.prefixes:
                if re.match(f"^{prefix}{name}\\b", msg.content.lower()):
                    command = prefix + name
                    break
            if command:
                break

        if len(command) == 0:
            return None

        if self.needsContent and len(msg.content[len(command) :].strip()) == 0:
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

        await self.execute_command(client, msg, msg.content[idx:].strip())
        return True

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")


from .ai import AI
from .code import Code
from .echo import Echo
from .lmdtfy import Lmdtfy, Lmgtfy
from .minecraft import Minecraft
from .translate import Translate

# Please keep in alphabetical order
all_commands = [AI(), Code(), Echo(), Lmdtfy(), Lmgtfy(), Minecraft(), Translate()]
