from dataclasses import dataclass

from aico.core import Project


@dataclass
class Stats:
    project: Project

    def files_qty(self) -> int:
        return len(self.project.files)

    def lines_of_code(self) -> int:
        return sum(len(c.split("\n")) for c in self.project.files_content.values())

    def characters(self):
        return sum(len(c) for c in self.project.files_content.values())

    def asdict(self):
        return {
            'files_qty': self.files_qty(),
            'lines_of_code': self.lines_of_code(),
            'characters': self.characters(),
        }