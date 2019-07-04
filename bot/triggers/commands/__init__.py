from .. import MessageTrigger


class Command(MessageTrigger):
    prefixes = ["!"]

    def is_valid(self, msg) -> int:
        idx = len(self.name)
        for prefix in self.prefixes:
            if msg.content.startswith(f"{prefix}{self.name} "):
                idx += len(prefix)
                break

        if idx == len(self.name):
            return None

        if msg.author.bot:
            return None

        try:
            if self.is_valid_command(msg):
                return idx
        except:
            return idx

    async def execute(self, msg) -> None:
        idx = self.is_valid(msg)
        if idx is None:
            return None

        await self.execute_command(msg, msg.content[idx + 1 :])

    async def execute_command(self, msg, content: str) -> None:
        raise NotImplementedError("'execute_command' not implemented for this command")
