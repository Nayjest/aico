import microcore as mc
from aico.core import project


def get_last_backup_number() -> int | None:
    backup_path = project().work_path / "backups"
    if not backup_path.is_dir():
        return None
    numeric_dirs = sorted(
        (int(folder.name) for folder in backup_path.iterdir() if folder.is_dir() and folder.name.isdigit()),
        reverse=True
    )
    return numeric_dirs[0] if numeric_dirs else None


def get_next_backup_folder():
    return project().work_folder / "backups" / str((get_last_backup_number() or 0) + 1)


def get_last_backup_folder():
    n = get_last_backup_number()
    return (project().work_folder / "backups" / str(n)) if n else None


def backup_src_folder():
    bckp_folder = get_next_backup_folder()
    print(f"Backing up src folder into {mc.storage.file_link(bckp_folder)}")
    ignore = project().ignore + [f"{i}*" for i in project().ignore]
    mc.storage.copy(
        project().src_folder,
        bckp_folder, ignore
    )


def rollback_src_folder():
    if not (bckp_folder := get_last_backup_folder()):
        raise ValueError("No backups found")
    print(f"Backing up src folder into {mc.storage.file_link(bckp_folder)}")
    ignore = project().ignore + [f"{i}*" for i in project().ignore]
    ignore = project().ignore + [f"{i}*" for i in project().ignore]
    mc.storage.copy(
        project().src_folder,
        bckp_folder, ignore
    )