import os
import subprocess
from pathlib import Path


def pull(repo_path: str | Path):
    result = subprocess.run(
        ["git", "pull"],
        cwd=repo_path,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    print(result.stdout)


def get_logs(repo_dir: str | Path, pull_changes=False, limit=20, oneline=False) -> str:
    repo_dir = Path(repo_dir)
    if not repo_dir.is_dir():
        raise ValueError(f"Directory {repo_dir} does not exist.")
    if pull_changes:
        print("Pulling the latest changes from the repository...")
        pull(repo_dir)
    print("Collecting commits...")
    result = subprocess.run(
        ["git", "log", "-n", str(limit)] + (["--oneline"] if oneline else []),
        cwd=repo_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )

    # Return the stdout of the command
    return result.stdout
