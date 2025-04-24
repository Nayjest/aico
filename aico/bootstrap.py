from aico.const import (
    WORK_FOLDER,
    AICO_MODULE_LOCATION,
    AICO_USER_HOME,
    IN_AICO_MODULE_FOLDER
)

import os
from pathlib import Path

import colorama
import typer
import microcore as mc
from microcore import ui

from aico.cli_ui import interactive_configure

ENV_FILE = os.getenv('AICO_ENV_FILE') or '.env'

def in_project_folder() -> bool: return Path(WORK_FOLDER).exists()

def find_env_file() -> str:
    print(f"Searching for {ENV_FILE}")
    path = Path(AICO_MODULE_LOCATION) / ENV_FILE
    if not path.exists():
        path = Path(WORK_FOLDER) / ENV_FILE
    if not path.exists():
        path = AICO_USER_HOME / ENV_FILE
    if not path.exists():
        path = Path(ENV_FILE)
    if not path.exists():
        raise mc.LLMConfigError(f"Can't find configuration file ({ENV_FILE})")
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
    try:
        mc.configure(
            STORAGE_PATH=determine_storage_path(),
            USE_LOGGING=USE_LOGGING,
            DOT_ENV_FILE=find_env_file(),
            PROMPT_TEMPLATES_PATH=AICO_MODULE_LOCATION / 'aico' / 'tpl',
            EMBEDDING_DB_FOLDER= f"{WORK_FOLDER}/chroma",
        )
        mc.logging.LoggingConfig.STRIP_REQUEST_LINES = None
    except mc.LLMConfigError as e:
        ui.error(e)
        if ui.ask_yn("Do you want to configure AICO now?", default=False):
            interactive_configure(AICO_USER_HOME / ENV_FILE)
        else:
            ui.error("Please, configure AICO using .env file")
        exit()


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