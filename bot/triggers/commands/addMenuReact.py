from .. import utils
from .. import ReactionTrigger


class AddMenuReact(ReactionTrigger):
    async def execute(self, client, reaction, usr):
        print(str(reaction))
