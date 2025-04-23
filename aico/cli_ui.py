from microcore.ui import ask_yn

from aico.const import AICO_USER_HOME
import microcore as mc
from microcore import ui, ApiType


def interactive_configure(file_path: str = None):
    raw_config = dict()
    raw_config["LLM_API_TYPE"] = ui.ask_choose(
        "Choose LLM API Type:",
        list(i.value for i in mc.ApiType if not ApiType.is_local(i)),
    )
    raw_config["LLM_API_KEY"] = ui.ask_non_empty("API Key: ")
    raw_config["MODEL"] = ui.ask_non_empty("Model Name: ")
    raw_config["LLM_API_BASE"] = input("API Base URL (may be empty for some API types): ")
    try:
        mc.configure(
            USE_DOT_ENV=False,
            STORAGE_PATH=AICO_USER_HOME,
            USE_LOGGING=True,
            **raw_config
        )
        print("Testing LLM...")
        q = "What is capital of France?\n(!) IMPORTANT: Answer only with one word"
        assert "pari" in mc.llm(q).lower()
    except Exception as e:
        mc.ui.error(f"Error testing LLM API: {e}")
        if ui.ask_yn("Restart configuring?"):
            interactive_configure(file_path)
            return
        else:
            return

    config_body = ''.join(f"{k}={v}\n" for k, v in raw_config.items())
    print(f"Configuration:\n{ui.yellow(config_body)}")
    if ask_yn("Save configuration to file?"):
        print(f"Saved to {mc.utils.file_link(file_path)}")
        with open(file_path, "w") as f:
            f.write(config_body)




