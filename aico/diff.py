import difflib
import subprocess
import sys
from pathlib import Path
import patch
from .core import env


def create_uni_diff(original_fn, updated_fn, diff_fn, src_root):
    with open(original_fn, 'r') as file1, open(updated_fn, 'r') as file2:
        file1_lines = file1.readlines()
        file2_lines = file2.readlines()
        target_fn = (
            Path(original_fn)
            .absolute()
            .relative_to(
                Path(src_root).absolute()
            )
            .__str__()
            .replace('\\', '/')
        )
        diff = difflib.unified_diff(file1_lines, file2_lines, fromfile=f"a/{target_fn}", tofile=f"b/{target_fn}")
        with open(diff_fn, 'w') as diff_file:
            diff_file.writelines(diff)
            diff_file.write('\n')


def apply_patch_cli(patch_file_name: str | Path, root_path: str | Path = None):
    file_name = (
        Path(patch_file_name)
        .absolute()
        .relative_to(Path(root_path).absolute())
        .__str__()
        .replace('\\', '/')
    )
    root_path = str(root_path).replace('\\', '/')
    if sys.platform.startswith("win"):
        patch_command = env().context.win_patch_command
    else:
        patch_command = "patch {}"
    patch_command = patch_command.format(
        f" -p1 --binary --ignore-whitespace -F3 -f -d {root_path}/ -i {file_name}"
    )
    print(patch_command)
    subprocess.run(patch_command, shell=True)


def apply_patch_py(patch_file_name: str | Path, root_path: str | Path = None):
    p = patch.fromfile(patch_file_name)
    p.apply(root=root_path)


def apply_patch(patch_file_name: str | Path, root_path: str | Path = None):
    apply_patch_py(patch_file_name, root_path)
    # apply_patch_cli(patch_file_name, root_path)