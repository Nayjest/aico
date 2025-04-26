import sys
from pathlib import Path

WORK_FOLDER = f".{__package__}"
DEFAULT_IGNORE = [
    WORK_FOLDER,
    '.git',
    '__pycache__',
    '.idea',
    'venv',
    '.pytest_cache',
    '.coverage',
    'coverage.xml',
    ".pylintrc",
    '.diff',
    '.patch',
    'node_modules',
    'package-lock.json',
    'dist',
]

AICO_MODULE_LOCATION = Path(__file__).parent.parent
if (AICO_MODULE_LOCATION / 'ai-microcore').exists():  # self-dev. feature
    sys.path.insert(0, Path(AICO_MODULE_LOCATION / 'ai-microcore').absolute().as_posix())

AICO_USER_HOME = Path('~/.aico_home').expanduser().absolute()

IN_AICO_MODULE_FOLDER = Path('aico').exists()
