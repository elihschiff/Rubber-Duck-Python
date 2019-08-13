from .test_ai import TestAI
from .test_code import TestCode
from .test_echo import TestEcho
from .test_help import TestHelp

# from .test_latex import TestLatex # latex machine broke
from .test_lmdtfy import TestLmdtfy
from .test_man import TestMan
from .test_mc import TestMinecraft
from .test_translate import TestTranslate

all_commands = [
    TestAI,
    TestCode,
    TestEcho,
    TestHelp,
    # TestLatex, # latex machine broke
    TestLmdtfy,
    TestMan,
    TestMinecraft,
    TestTranslate,
]