import fnmatch
import os


def list_dir(path: str, ignore=None) -> list[str]:
    if ignore is None:
        ignore = ['.git', ]
    files_list = []
    for root, dir, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if not any(fnmatch.fnmatch(file_path, '*' + p + '*') for p in ignore):
                files_list.append(file_path.replace(str(path) + os.sep, '').replace(os.sep, '/'))
    return files_list

