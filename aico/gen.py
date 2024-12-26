from .bootstrap import *
from .core import project
import rich
from colorama import Fore as C

mc.use_logging()

def rollback():
    from .backup import rollback_src_folder
    rollback_src_folder()

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

    if files or deleted_files:
        from .backup import backup_src_folder
        backup_src_folder()

    for f in files:
        mc.storage.write(f"{project().src_folder}/{f['file_path']}", f['file_content'], backup_existing=False)

    for f in deleted_files:
        mc.storage.delete(f"{project().src_folder}/{f}")

    work_data["steps"].append({
        "query": query,
        "original_user_query": original_user_query,
        "files": [i['file_path'] for i in files]
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
