import sys
sys.path.append('./ai-microcore')

import colorama
import typer
import microcore as mc

colorama.init(autoreset=True)
app = typer.Typer()
HOME_DIR = 'data'
mc.configure(
    STORAGE_PATH=HOME_DIR,
    USE_LOGGING=False,
    DOT_ENV_FILE='.env',
    LLM_DEFAULT_ARGS={
        'temperature': 0.2,
    },
)