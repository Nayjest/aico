import json
from pathlib import Path
import time
import rich
from colorama import Fore as C
from openai import APIError

import microcore as mc
from microcore.utils import file_link
from aico.core import env
from aico.diff import apply_patch_cli, create_uni_diff, apply_patch


def decide_on_change(change: dict):
    return (
        'estimation' not in change
        or 'decision' not in change['estimation']
        or "reject" not in str(change['estimation']['decision']).lower()
    )


def apply_changes(structured_result: str | dict):
    if isinstance(structured_result, str):
        structured_result = mc.storage.read_json(structured_result)
    for item in structured_result['changes']:
        try:
            if not decide_on_change(item):
                print(f"Skipping patch {item['number']}")
                continue
            print(f"Applying patch {item['number']} from {mc.storage.file_link(item['diff_file'])}")
            apply_patch(
                f"{mc.config().STORAGE_PATH}/{item['diff_file']}",
                env().project.src_path
            )
        except Exception as e:
            mc.ui.error(f"Error applying patch {item['number']}: {e}")


def apply_changes_interactive(structured_result: str | dict):
    if isinstance(structured_result, str):
        structured_result = mc.storage.read_json(structured_result)
    items = structured_result['changes']
    messages = ["Do nothing"] + [item['message'] for item in items] + ["Apply all"]
    if items:
        message = ""
        while message != "Do nothing":
            message = mc.ui.ask_choose("Choose fix to apply", messages)
            if message == "Apply all":
                for item in items:
                    print(f"Applying patch {item['diff_file']}")
                    apply_patch_cli(
                        f"{mc.config().STORAGE_PATH}/{item['diff_file']}",
                        env().project.src_path
                    )
                    return
            for item in items:
                if item['message'] == message:
                    print(f"Applying patch {item['diff_file']}")
                    apply_patch_cli(
                        f"{mc.config().STORAGE_PATH}/{item['diff_file']}",
                        env().project.src_path
                    )
                    messages.remove(message)
                    if len(messages) == 2:
                        return


def process_file(file_name: str | Path, verbose=True):
    proj = env().project
    prompt = mc.SysMsg(mc.tpl('file-review-full-content.j2', file_name=file_name, project=proj))

    class Token:
        ITEM_BEGIN = '[[---ITEM_BEGIN---]]'
        ITEM_END = '[[---ITEM_END---]]'
        NO_CHANGES = '[[---NO_CHANGES---]]'

    # File paths
    out_dir = Path(proj.work_folder) / 'out'
    base_fn = file_name.replace('/', '_').replace('.', '_')
    ai_text_fn = f"{out_dir}/{base_fn}.ai-text"
    structured_result_fn = f"{out_dir}/{base_fn}.json"

    mc.storage.clean(out_dir)

    try_num = 0
    out = ""
    while True:
        try:
            try_num += 1
            if try_num > 3:
                return {"result": "LLM_INCORRECT_RESPONSE"}
            out = mc.llm(prompt)
            mc.storage.write(ai_text_fn, out, rewrite_existing=True)
            items = []
            if not Token.ITEM_BEGIN in out:
                break
            out = out.replace(Token.NO_CHANGES, '')
            out_parts = (
                out
                .replace('\n' + Token.ITEM_END, '')
                .replace(Token.ITEM_END, '')
                .split(Token.ITEM_BEGIN + '\n')[1:]
            )
            item_num = 0
            for part in out_parts:
                item_num += 1
                updated_fn = f"{out_dir}/{base_fn}-{item_num}.orig"
                diff_fn = f"{out_dir}/{base_fn}-{item_num}.patch"
                item = dict(
                    number=item_num,
                    file_name=file_name,
                    **mc.parse(part, required_fields=['message', 'updated_file_content'])
                )
                mc.storage.write(updated_fn, item['updated_file_content'], rewrite_existing=True)
                create_uni_diff(
                    proj.src_path / file_name,
                    mc.storage.path / updated_fn,
                    mc.storage.path / diff_fn,
                    proj.src_path
                )
                item['diff_file'] = diff_fn
                item['diff'] = mc.storage.read(diff_fn)
                items.append(item)
            break
        except mc.BadAIAnswer as e:
            mc.ui.error(f"Bad AI Answer: {e}, Retrying [{try_num}]...")
            print(f"LLM Response:\n{C.GREEN}{out}")
            ...

    verbose and rich.print(items)
    structured_result = dict(
        changes=items,
        model=mc.config().MODEL,
        affected_files=[file_name]
    )
    mc.storage.write_json(structured_result_fn, structured_result, rewrite_existing=True)
    return structured_result


def file_cr_generate_changes(file_name: str | Path, verbose=True, clean_dir=True) -> str:
    prj = env().project
    print(f"Generating Code Review Changes for {prj.file_link(file_name)}...")
    prompt = mc.SysMsg(mc.tpl('cr-file-gen-changes.j2', file_name=file_name, project=prj))

    class Token:
        ITEM_BEGIN = '[[---ITEM_BEGIN---]]'
        ITEM_END = '[[---ITEM_END---]]'
        NO_CHANGES = '[[---NO_CHANGES---]]'

    # File paths
    out_dir = Path(prj.work_folder) / 'out'
    base_fn = file_name.replace('/', '_').replace('.', '_')
    ai_text_fn = f"{out_dir}/{base_fn}.ai-text"
    structured_result_fn = f"{out_dir}/{base_fn}.json"
    if clean_dir:
        mc.storage.clean(out_dir)

    try_num = 0
    out = ""
    while True:
        try:
            try_num += 1
            if try_num > 1+env().context.code_review.retries_if_nothing_found:
                return {"result": "LLM_INCORRECT_RESPONSE"}
            out = mc.llm(prompt)
            mc.storage.write(ai_text_fn, out, rewrite_existing=True)
            items = []
            if Token.ITEM_BEGIN not in out:
                if Token.NO_CHANGES in out:
                    if try_num <= env().context.code_review.retries_if_nothing_found:
                        print(
                            f"Retrying (no changes) "
                            f"[{try_num}/{env().context.code_review.retries_if_nothing_found}]..."
                        )
                        continue
                break
            out = out.replace(Token.NO_CHANGES, '')
            out_parts = (
                out
                .replace('\n' + Token.ITEM_END, '')
                .replace(Token.ITEM_END, '')
                .split(Token.ITEM_BEGIN + '\n')[1:]
            )
            item_num = 0
            for part in out_parts:
                item_num += 1
                item = dict(
                    number=item_num,
                    file_name=file_name,
                    **mc.parse(part, required_fields=['short_info', 'implementation_details'])
                )
                items.append(item)
            break
        except mc.BadAIAnswer as e:
            mc.ui.error(f"Bad AI Answer: {e.message}, Retrying [{try_num}]...")
            print(f"LLM Response:\n{C.GREEN}{out}")

    verbose and rich.print(items)
    structured_result = dict(
        changes=items,
        model=mc.config().MODEL,
        affected_files=[file_name]
    )
    mc.storage.write_json(structured_result_fn, structured_result, rewrite_existing=True)
    print("Results stored in "+mc.storage.file_link(structured_result_fn))
    return structured_result_fn


def provide_implementation(change: dict):
    proj = env().project
    file_name = change['file_name']
    item_num = change['number']
    prompt = mc.tpl(
        'task-update-file.j2',
        file_name=file_name,
        project=proj,
        task=f"Short info:\n{change['short_info']}\nImplementation details:\n{change['implementation_details']}\n"
    )
    try_num = 0
    out = ""
    while True:
        try:
            try_num += 1
            if try_num > 3:
                return {"result": "LLM_INCORRECT_RESPONSE"}
            out = mc.llm(prompt)
            fc = mc.parse(out, required_fields=['begin_new_file_content'])['begin_new_file_content']
            break
        except mc.BadAIAnswer as e:
            mc.ui.error(f"Bad AI Answer: {e.message}, Retrying [{try_num}]...")
            print(f"LLM Response:\n{C.GREEN}{out}")
        except APIError as e:
            sleep = 30
            mc.ui.error(f"API Error {e}, Retrying after {sleep} sec[{try_num}]...")
            time.sleep(sleep)
    out_dir = Path(proj.work_folder) / 'out'
    base_fn = file_name.replace('/', '_').replace('.', '_')

    updated_fn = f"{out_dir}/{base_fn}-ch{item_num}.new"
    mc.storage.write(updated_fn, fc, rewrite_existing=True)
    diff_fn = f"{out_dir}/{base_fn}-ch{item_num}.patch"

    create_uni_diff(
        proj.src_path / file_name,
        mc.storage.path / updated_fn,
        mc.storage.path / diff_fn,
        proj.src_path
    )
    change['diff_file'] = diff_fn
    change['diff'] = mc.storage.read(diff_fn)
    return change


def provide_implementations(structured_result_fn):
    structured_result = mc.storage.read_json(structured_result_fn)
    items = structured_result['changes']
    for i in range(len(items)):
        if not decide_on_change(items[i]):
            print(f"Skipping implementing rejected change #{items[i]['number']}")
            continue
        print(
            f"{C.MAGENTA} Implementing change "
            f"#{items[i]['number']}/{len(items)} [{C.WHITE} {items[i]['short_info']} {C.MAGENTA}]..."
        )
        items[i] = provide_implementation(items[i])
        mc.storage.write_json(structured_result_fn, structured_result, backup_existing=False)
    print("Implementations ready")
    return structured_result


def self_estimate_changes(structured_result_fn, rewrite = True):
    structured_result = mc.storage.read_json(structured_result_fn)
    try_num = 0
    out = ""
    old_changes = structured_result['changes']
    if len(old_changes) == 0:
        return structured_result
    while True:
        try:
            try_num += 1
            if try_num > 3:
                return {"result": "LLM_INCORRECT_RESPONSE"}

            updated_changes = mc.tpl(
                'self-estimate-changes.j2',
                data=json.dumps(structured_result, indent=2),
                project=env().project,
                file_name=structured_result['affected_files'][0]
            ).to_llm().parse_json(required_fields=['changes'])['changes']
            for i in range(len(old_changes)):
                if old_changes[i]['number'] != updated_changes[i]['number']:
                    raise Exception("Change Numbers mismatch")
                old_changes[i]['estimation'] = updated_changes[i]['estimation']
            break
        except Exception as e:
            mc.ui.error(f"Bad AI Answer: {str(e)}, Retrying [{try_num}]...")
            print(f"LLM Response:\n{C.GREEN}{out}")
    if rewrite:
        mc.storage.write_json(structured_result_fn, structured_result, backup_existing=False)
    return structured_result