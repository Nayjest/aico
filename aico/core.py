import aico.bootstrap
import logging
import microcore as mc
from dataclasses import dataclass, field, asdict
from pathlib import Path
from colorama import Fore as C

from .const import WORK_FOLDER, DEFAULT_IGNORE
from .utils import list_dir


@dataclass
class CodeReviewSettings:
    retries_if_nothing_found: int = 2


@dataclass
class GenerationSettings:
    backup_src_folder: bool = False


@dataclass
class Context:
    project_root: Path
    win_patch_command: str = "\"C:\\Program Files\\Git\\bin\\bash.exe\" -c \"patch {}\""
    code_review: CodeReviewSettings = field(default=None)
    generation: GenerationSettings = field(default=None)

    @staticmethod
    def load():
        params = mc.storage.read_json('context.json')
        params['project_root'] = Path(params['project_root'])
        params['code_review'] = CodeReviewSettings(**params.get('code_review', {}))
        params['generation'] = GenerationSettings(**params.get('generation', {}))
        return Context(**params)


@dataclass
class Project:
    src_folder: str | Path
    work_folder: str | Path
    ignore: list[str]
    bot_personality: str = ""

    _files_content: dict[str, str] | None = None
    _meta = None

    @property
    def src_path(self) -> Path:
        return mc.storage.path / self.src_folder

    @property
    def work_path(self) -> Path:
        return mc.storage.path / self.work_folder

    @property
    def work_file(self) -> str | Path:
        return self.work_folder / "work.json"

    @property
    def work_data(self) -> dict:
        return mc.storage.read_json(self.work_file, default={"steps": []})

    def save_work_data(self, value: dict):
        mc.storage.write_json(
            self.work_file,
            value,
            backup_existing=False,
        )

    def file_link(self, file_name: str):
        return mc.utils.file_link(self.src_path / file_name)

    @property
    def meta(self) -> dict:
        if not self._meta:
            self._meta = mc.storage.read_json(f'{self.work_folder}/meta.json')
        return self._meta

    @property
    def files(self) -> list[str]:
        return list_dir(str(self.src_path), self.ignore)

    @property
    def not_empty_files(self):
        res = []
        for f,c in self.files_content.items():
            if len(c.strip()) <= 1:
                continue
            res.append(f)
        return res

    @property
    def files_content(self) -> dict[str, str]:
        if not self._files_content:
            self._files_content = {}
            for f in self.files:
                try:
                    self._files_content[f] = mc.storage.read(f"{self.src_folder}/{f}")
                except Exception:
                    logging.error(f"{C.RED}Error reading file {f}{C.RESET}")
        return self._files_content

    def __post_init__(self):
        self.src_folder = Path(self.src_folder)
        self.work_folder = Path(self.work_folder)

    @staticmethod
    def load():
        project_root = env().context.project_root
        work_folder = project_root / WORK_FOLDER
        project_file = work_folder / "project.json"
        if mc.storage.exists(project_file):
            return Project(**mc.storage.read_json(project_file))
        else:
            params = {
                "src_folder": str(project_root),
                "work_folder": str(work_folder),
                "ignore": DEFAULT_IGNORE,
            }
            mc.storage.write_json(project_file, params)
            return Project.load()

    @staticmethod
    def make(name: str, **kwargs):
        args = {
            "src_folder": name,
            "work_folder": f"{name}/{WORK_FOLDER}",
            "ignore": DEFAULT_IGNORE,
            **kwargs
        }
        return Project(**args)

    def asdict(self):
        return {
            k: str(v.as_posix()) if isinstance(v, Path) else v
            for k, v in asdict(self).items()
            if not k.startswith('_')
        }

    def save(self):
        # @todo use work_path?
        mc.storage.write_json(f'{self.work_folder}/project.json', self.asdict(), backup_existing=False)

    def exists(self) -> bool:
        # @todo use work_path? project file?
        return mc.storage.exists(f'{self.work_folder}/project.json')



@dataclass
class _Env:
    storage_path: str = "data"
    context: Context = field(default_factory=Context.load)
    project: Project = None
    instance: "_Env" = None

    def __post_init__(self):
        _Env.instance = self
        self.project = Project.load()


def env() -> _Env:
    return _Env.instance or _Env()  # noqa


def project() -> Project:
    return env().project


def config() -> Context:
    return env().context
