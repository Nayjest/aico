from collections import deque
import microcore as mc
from aico.core import project
from microcore import UserMsg

mem = deque(maxlen=100)


def chat():
    p = project()
    work_file = f"{p.work_folder}/work.json"
    while q := UserMsg(input(">> ")):

        work_data = mc.storage.read_json(work_file, default={"steps": []})
        steps = work_data["steps"]