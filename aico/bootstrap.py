import os
import sys
from pathlib import Path

import colorama
import typer

AICO_MODULE_LOCATION = Path(__file__).parent.parent
if (AICO_MODULE_LOCATION / 'ai-microcore').exists():  # self-dev. feature
    sys.path.insert(0, (AICO_MODULE_LOCATION / 'ai-microcore').absolute().as_posix())

import microcore as mc

AICO_USER_HOME = Path('~/.aico_home').expanduser().absolute()

IN_AICO_MODULE_FOLDER = Path('aico').exists()
ENV_FILE = os.getenv('ENV') or '.env'

def in_project_folder() -> bool: return Path('.aico').exists()

def find_env_file() -> str:
    global ENV_FILE
    print(f"Searching for {ENV_FILE}")
    path = Path(AICO_MODULE_LOCATION) / ENV_FILE
    if not path.exists():
        path = Path('.aico') / ENV_FILE
    if not path.exists():
        path = AICO_USER_HOME / ENV_FILE
    if not path.exists():
        path = Path(ENV_FILE)
    print(f"ENV: {str(path.absolute().as_posix())}")
    return str(path.absolute().as_posix())

def determine_storage_path() -> Path:
    if in_project_folder():
        return Path.cwd()
    if IN_AICO_MODULE_FOLDER:
        return Path('data')
    return AICO_USER_HOME

def bootstrap():
    global USE_LOGGING
    colorama.init(autoreset=True)
    mc.configure(
        STORAGE_PATH=determine_storage_path(),
        USE_LOGGING=USE_LOGGING,
        DOT_ENV_FILE=find_env_file(),
        PROMPT_TEMPLATES_PATH=AICO_MODULE_LOCATION / 'tpl',
    )

app = typer.Typer()
USE_LOGGING = True
@app.callback()
def main(
    env: str = typer.Option(
        None,
        help="Specify the environment file to use (overrides default)",
    ),
    silent: bool = typer.Option(
        None,
        help="no llm output",
    )
):
    global ENV_FILE, USE_LOGGING
    if env:
        ENV_FILE = f".env.{env}" if ".env." not in env else env
        print(f"OVERRIDE {ENV_FILE}")
    if silent:
        USE_LOGGING = False
    bootstrap()