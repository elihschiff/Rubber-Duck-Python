from .. import MessageTrigger


class Command(MessageTrigger):
    prefixes = ["!"]

    def is_valid(self, msg) -> int:
        idx = len(self.name)
        for prefix in self.prefixes:
            if msg.content.startswith(f"{prefix}{self.name}"):
                idx += len(prefix) + 1
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

    async def execute(self, client, msg) -> bool:
        idx = self.is_valid(msg)
        if idx is None:
            return False

        await self.execute_command(client, msg, msg.content[idx + 1 :])
        return True

    async def execute_command(self, client, msg, content: str):
        raise NotImplementedError("'execute_command' not implemented for this command")
