from aico.bootstrap import app, in_project_folder, ENV_FILE
from aico.backup import backup_src_folder
import threading
import time
import webbrowser

from aico.cli_ui import interactive_configure
from aico.git import get_logs
from aico.stats import Stats

import os
import subprocess
from aico.file_processing import process_file, apply_changes_interactive, file_cr_generate_changes, \
    provide_implementations, \
    self_estimate_changes, apply_changes
import re
from aico.core import *
import microcore as mc
import typer
from colorama import Fore as C
import rich
import aico.gen
from microcore import ui
from rich.pretty import pprint


@app.command()
def use(project_name: str):
    ctx = Context.load()
    ctx.project_root = project_name if not in_project_folder() else str(Path.cwd().resolve())
    p = Project.make(project_name)
    if not p.exists():
        mc.ui.error(f"Project \"{project_name}\" not found.")
        return
    print(f"Activating \"{project_name}\" project...")
    ctx.save()

    print(mc.utils.file_link(f"{p.src_path}"))

@app.command(name='configure', help="Configure the Language model", hidden=True)
def cli_configure():
    interactive_configure(AICO_USER_HOME / ENV_FILE)

@app.command(name='new_project', help="Alias of new-project", hidden=True)
@app.command(name='create-project', help="Alias of new-project", hidden=True)
@app.command(name='create_project', help="Alias of new-project", hidden=True)
@app.command(name='make-project', help="Alias of new-project", hidden=True)
@app.command(name='make_project', help="Alias of new-project", hidden=True)
@app.command(name='init-project', help="Alias of new-project", hidden=True)
@app.command(name='init_project', help="Alias of new-project", hidden=True)
@app.command(name='init', help="Alias of new-project", hidden=True)
@app.command(help="Creates a new project and sets it as the current active project.")
def new_project(
        name: str="",# = typer.Option(
        #    ..., "--name", "-n", prompt="Enter project name", show_default=False
        #),
        git: bool = None,
        here: bool = None,
):
    if in_project_folder():
        mc.ui.error("Already in a project folder. Switching to it.")
        use(Path.cwd().name)
        return
    if here is None:
        if not in_project_folder():
            here = mc.ui.ask_yn(
                f"Initialize new project in current folder {mc.utils.file_link(Path.cwd())}?\n"
                +ui.gray('(otherwise AICO data folder will be used)\n')
            )
            if here is None:
                mc.ui.error("Exiting.")
                return
    if here:
        name = name or Path.cwd().name
    if not name:
        name = mc.ui.ask_non_empty("Enter project name: ")

    params = {
        "name": name,
    }
    if here:
        params["src_folder"] = '.'
        params["work_folder"] = WORK_FOLDER
        mc.config().STORAGE_PATH = Path.cwd()
    p = Project.make(**params)
    if p.exists():
        mc.ui.error(f"Project \"{name}\" already exists.")
        change = mc.ui.ask_yn(f"Switch to existing \"{name}\" project?", )
        if change:
            mc.ui.error(f"Not implemented.")
        else:
            print("No changes made. Exiting.")
        return
    print(f"Creating project \"{name}\"...")
    p.save()

    if git:
        print(f"Initializing git...")
        mc.storage.copy(
            Path(__file__).parent.parent / 'presets' / 'git',
            p.src_path.relative_to(mc.storage.path)
        )


    use(name)
    print(f"Done.")

@app.command(help="list project files (without ignored)")
@app.command(name='files-list',hidden=True)
def list_files():
    files = project().files
    rich.print(files)
    print(f"Total: {len(files)} files")


@app.command(help="Generates additional project metadata in <.aico>/meta.json using LLM")
def describe():
    q = mc.tpl('describe.j2', project=project())
    out = mc.llm(q, callback=lambda text: print(text, end=''))
    mc.storage.write_json(f'{project().work_folder}/meta.json', out.parse_json())
    print("Metadata saved")
    # mc.tpl('collect-meta.j2', input = mc.tpl('')).to_llm(

@app.command(help="Shows configuration of current project")
def status():
    project()
    try:
        pprint(project())
    except FileNotFoundError:
        print(mc.utils.dedent(f"""
        Status: {mc.ui.magenta('Not initialized.')}
        \tenv file: {mc.config().DOT_ENV_FILE}
        \tmodel: {mc.config().MODEL}
        \tstorage: {mc.config().STORAGE_PATH}
        """))

@app.command(help='Shows project statistics')
def stats():
    stats = Stats(project())
    pprint(stats.asdict())

@app.command()
def improve():
    files = project().files
    print(files)

    out = ""
    for f, c in project().files_content.items():
        out += "====== FILE: " + f + ":\n"
        out += c + "\n"

    # print(len(out.split("\n")))

    processed = mc.tpl('one-improvement.j2', input=out, temperature=0).to_llm()
    print(processed)
    parse_and_rewrite(processed)


@app.command()
def files():
    mc.configure(STORAGE_PATH='data', USE_LOGGING=False)
    files_list = project().not_empty_files
    outs = {}
    i = 0
    for file_name in files_list:
        i += 1
        try:
            print(f"Processing [{i}/{len(files_list)}]: {C.CYAN}{file_name}{C.RESET}...\t", end='')
            out = process_file(file_name, autoapply=True, verbose=True)
            if "file_content" in out:
                del out["file_content"]
            print(f"{C.MAGENTA}{out['result']}")
            outs[file_name] = out
        except Exception as e:
            mc.ui.error(f"Error: {e}")
            raise e
        mc.storage.write_json(f'{project().work_folder}/files_out.json', outs, rewrite_existing=True)
    mc.storage.write_json(f'{project().work_folder}/files_out.json', outs, rewrite_existing=True)


def choose_file_if_needed(file_name: str):
    if not file_name or file_name not in project().not_empty_files:
        if file_name:
            print(f"{C.RED} File {file_name} not exists, choose another")
        file_name = mc.ui.ask_choose("Choose file", project().files)
    return file_name


@app.command()
def file(file_name: str = typer.Argument(None)):
    file_name = choose_file_if_needed(file_name)
    structured_result = process_file(file_name)
    apply_changes_interactive(structured_result)


@app.command()
def files_ms(apply: bool = typer.Option(True, help="Apply changes to project files")):
    files_list = project().not_empty_files
    out_dir = Path(project().work_folder) / 'out'
    mc.storage.clean(out_dir)

    for file_name in files_list:
        file_ms(file_name, clean_dir=False, apply=apply)


@app.command()
def file_ms(file_name: str = typer.Argument(None), clean_dir=True, apply=True):
    file_name = choose_file_if_needed(file_name)
    # print(f"Generating changes for {file_name}...")
    structured_result_fn = file_cr_generate_changes(file_name, clean_dir=clean_dir)
    if not isinstance(structured_result_fn, str):
        mc.ui.error("Error generating changes: no result file")
        return
    print("Estimating changes...")
    self_estimate_changes(structured_result_fn)
    print("Working on change implementations")
    provide_implementations(structured_result_fn)
    rich.print(mc.storage.read_json(structured_result_fn))
    if apply:
        print("Applying changes...")
        apply_changes(structured_result_fn)
    print('file_ms: finished')


@app.command()
def pull():
    os.chdir(project().src_path)
    result = subprocess.run(["git", "pull"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print(result.stdout)

@app.command()
def backup():
    os.chdir(project().src_path)
    backup_src_folder()

def parse_and_rewrite(input_text):
    # Regular expressions for extracting sections
    info_pattern = r"=====INFO=====\s*(.*?)\s*=====FILENAME====="
    filename_pattern = r"=====FILENAME=====\s*(.*?)\s*=====CONTENT====="
    content_pattern = r"=====CONTENT=====\s*(.*?)\s*(?=====|$)"

    # Extracting sections using regex
    info_match = re.search(info_pattern, input_text, re.DOTALL)
    filename_match = re.search(filename_pattern, input_text, re.DOTALL)
    content_match = re.search(content_pattern, input_text, re.DOTALL)

    if not filename_match or not content_match:
        print("Filename or content not found in the input text.")
        return

    filename = filename_match.group(1).strip()
    content = content_match.group(1).strip()

    # Optionally, use info
    info = info_match.group(1).strip() if info_match else "No description provided."

    # Rewrite the file with the new content
    with open(project().src_path / filename, 'w') as file:
        file.write(content)


def open_browser():
    time.sleep(1)
    webbrowser.open("http://localhost:5000")


@app.command()
def report():
    # Dynamically import webapp only when needed to avoid distribution issues
    from webapp.app import webapp
    threading.Thread(target=open_browser, daemon=True).start()
    webapp.run(debug=False, use_reloader=False)


@app.command()
def make_release_message(details: str = ""):
    logs = get_logs(env().project.src_path, limit=20)
    # language=Jinja2

    out = mc.prompt(
        """
Make a release message based on the git log.
Ignore commits before previous release.
Use Markdown syntax.
Do not include links to commits to changelog.
{{ details }}
{{ logs }}
        """,
        logs=logs,
        details=details
    ).to_llm()
    print(out)


if __name__ == "__main__":
    app()
