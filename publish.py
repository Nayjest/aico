import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

token = os.getenv("PYPI_TOKEN")
if not token:
    raise RuntimeError("PYPI_TOKEN is not set in .env")

subprocess.run([
    "python", "-m", "twine", "upload", "dist/*",
    "-u", "__token__",
    "-p", token,
    "--verbose"
])
