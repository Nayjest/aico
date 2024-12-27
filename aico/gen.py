from dataclasses import dataclass

from .bootstrap import *
from .core import project
import rich
from rich.pretty import pprint
from colorama import Fore as C

mc.use_logging()

@app.command(help="Rewrites project files with latest available backup.")
@app.command(name='rb-files', hidden=True)
@app.command(name='rb-fs', hidden=True)
@app.command(name='rollback-fs', hidden=True)
def rollback_files():
    from .backup import rollback_src_folder
    path = rollback_src_folder()

@app.command(help="Rolls back last step, restores files and deletes backup")
def rollback():
    wd = project().work_data
    step = wd["steps"][-1]

    print(f"Rolling back step:")
    pprint(pprint(step))

    wd["steps"] = wd["steps"][:-1]
    project().save_work_data(wd)
    rollback_files()
    backup_path = step["created_backup"]
    print(f"Deleting backup {backup_path}")
    mc.storage.delete(backup_path)
    return step

@app.command(help="Redo last step")
def redo():
    last_step = rollback()
    work(last_step['query'])


@dataclass
class ChangeList:
    files: list[dict]
    deleted_files: list[dict]

    def is_empty(self) -> bool:
        return not self.files and not self.deleted_files

    def apply(self):
        for f in self.files:
            mc.storage.write(f"{project().src_folder}/{f['file_path']}", f['file_content'], backup_existing=False)

        for f in self.deleted_files:
            mc.storage.delete(f"{project().src_folder}/{f}")

def generate_changelist(query: str):
    work_data = project().work_data
    tries = 0
    while True:
        try:
            tries += 1
            out = mc.tpl('gen/work.j2', query=query, project=project(), steps=work_data['steps']).to_llm()
            parts = out.split('[[BEGIN_FILE]]\n')[1:]
            parts = [i.split('[[END_FILE]]')[0] for i in parts]
            files = [
                mc.parse(i, r"\[(.*?)\]", required_fields=['file_path', 'file_content'])
                for i in parts
            ]

            parts = out.split('[[DELETE_FILE]]\n')[1:]
            deleted_files = [i.split('\n')[0] for i in parts]
            break
        except mc.BadAIAnswer as e:
            mc.ui.error(e)
            if tries > 3:
                mc.ui.error(f"Too many tries ({tries}), exiting")
                raise e

    return ChangeList(files=files, deleted_files=deleted_files)

@app.command()
def work(
        query: list[str] = typer.Argument(...),
        td: bool = typer.Option(
            False,
            help='Ask LLM to provide technical task description for user request'
        )
):
    if isinstance(query, list):
        query = " ".join(query)
    if td:
        res = make_td([query])
        query = res['technical_task_description']
        original_user_query = res['query']
    else:
        original_user_query = query
    changes = generate_changelist(query)
    if changes.is_empty():
        print(f"{C.RED}No changes detected, exiting{C.RESET}")

    from .backup import backup_src_folder
    created_backup: Path = backup_src_folder()
    changes.apply()

    work_data = project().work_data
    work_data["steps"].append({
        "query": query,
        "original_user_query": original_user_query,
        "files": [i['file_path'] for i in changes.files],
        "created_backup": created_backup.as_posix()
    })
    project().save_work_data(work_data)


@app.command()
def make_td(query: list[str] = typer.Argument(...)):
    if isinstance(query, list):
        query = " ".join(query)
    work_data = project().work_data
    out = mc.tpl(
        'gen/make-td.j2',
        query=query,
        project=project(),
        steps=work_data['steps']
    ).to_llm().parse_json(required_fields=["query", "technical_task_description"])
    print(f"{C.MAGENTA}Generated Technical task description:{C.RESET}: {out['technical_task_description']}")
    return out
