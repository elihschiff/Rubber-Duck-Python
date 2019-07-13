from .test_commands import all_commands

all_triggers = all_commands

from .test_quack import TestQuack
from .test_welcome import TestWelcome

all_triggers.append(TestQuack)
all_triggers.append(TestWelcome)
