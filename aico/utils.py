import fnmatch
from pathlib import Path


def list_dir(path: str | Path, ignore: list[str] | None = None) -> list[str]:
    ignore = ignore or ['.git']
    root = Path(path).expanduser().resolve()
    def _skip(rel: str, name: str) -> bool:
        return any(
            fnmatch.fnmatchcase(rel, p)
            or fnmatch.fnmatchcase(rel, f"{p}/*")
            or fnmatch.fnmatchcase(rel, f"*/{p}")
            or fnmatch.fnmatchcase(rel, f"*/{p}/*")
            or fnmatch.fnmatchcase(name, p)
            for p in ignore
        )
    return sorted(
        rel
        for f in root.rglob('*') if f.is_file()
        if not _skip((rel := f.relative_to(root).as_posix()), f.name)
    )
