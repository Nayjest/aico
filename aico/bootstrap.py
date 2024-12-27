import sys
from pathlib import Path

import colorama
import typer

AICO_MODULE_LOCATION = Path(__file__).parent.parent
if (AICO_MODULE_LOCATION / 'ai-microcore').exists():
    sys.path.insert(0, (AICO_MODULE_LOCATION / 'ai-microcore').absolute().as_posix())

import microcore as mc

AICO_USER_HOME = Path('~/.aico_home').expanduser().absolute()

IN_AICO_MODULE_FOLDER = Path('aico').exists()

def in_project_folder() -> bool: return Path('.aico').exists()

def find_env_file() -> str:
    path = Path('.env')
    if not path.exists():
        path = Path('.aico') / '.env'
    if not path.exists():
        path = AICO_USER_HOME / '.env'
    if not path.exists():
        path = Path(AICO_MODULE_LOCATION) / '.env'
    return str(path.absolute().as_posix())

def determine_storage_path() -> Path:
    if in_project_folder():
        return Path.cwd()
    if IN_AICO_MODULE_FOLDER:
        return Path('data')
    return AICO_USER_HOME


def bootstrap():
    colorama.init(autoreset=True)
    app = typer.Typer()
    mc.configure(
        STORAGE_PATH=determine_storage_path(),
        USE_LOGGING=False,
        DOT_ENV_FILE=find_env_file(),
        # LLM_DEFAULT_ARGS={
        #     'temperature': 0.2,
        # },
        PROMPT_TEMPLATES_PATH=AICO_MODULE_LOCATION / 'tpl',
    )
    return app
app = bootstrap()