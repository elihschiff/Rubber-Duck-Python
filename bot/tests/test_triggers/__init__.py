from .test_commands import all_commands

all_triggers = all_commands

from .test_quack import TestQuack

all_triggers.append(TestQuack)
