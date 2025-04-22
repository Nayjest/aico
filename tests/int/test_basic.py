import sys
from pathlib import Path
import os
import json
import shutil

def test_new_project(tmp_path):
    # Ensure tests/temp/proj is the working directory for project creation
    tests_temp = Path(__file__).parent.parent / "temp"
    proj_dir = tests_temp / "proj"
    shutil.rmtree(proj_dir, ignore_errors=True)
    proj_dir.mkdir(parents=True, exist_ok=True)

    prev_cwd = os.getcwd()
    try:
        os.chdir(proj_dir)
        sys.path.insert(0, str((Path(__file__).parent.parent.parent / 'aico').resolve()))
        import aico.main as aico_main
        from typer.testing import CliRunner
        runner = CliRunner()
        # Use cwd parameter to force Typer's runner to work in this directory too
        result = runner.invoke(aico_main.app, ["new-project", "--name", "proj", "--here"], catch_exceptions=False)
        # Did project.json get created?
        project_meta = proj_dir / ".aico" / "project.json"
        assert result.exit_code == 0, f"CLI failed (code {result.exit_code}):\n{result.output}"
        assert project_meta.exists(), f"Expected {project_meta} to be created"
        data = json.loads(project_meta.read_text())
        assert data["src_folder"] == ".", "src_folder should be '.'"
        assert ".aico" in data["work_folder"], f"work_folder not .aico: {data['work_folder']}"
    finally:
        os.chdir(prev_cwd)
        shutil.rmtree(tests_temp, ignore_errors=True)

def test_status(tmp_path):
    tests_temp = Path(__file__).parent.parent / "temp"
    proj_dir = tests_temp / "proj2"
    shutil.rmtree(proj_dir, ignore_errors=True)
    proj_dir.mkdir(parents=True, exist_ok=True)
    prev_cwd = os.getcwd()
    try:
        os.chdir(proj_dir)
        sys.path.insert(0, str((Path(__file__).parent.parent.parent / 'aico').resolve()))
        import aico.main as aico_main
        from typer.testing import CliRunner
        runner = CliRunner()
        runner.invoke(aico_main.app, ["new-project", "--name", "proj2", "--here"], catch_exceptions=False)
        result = runner.invoke(aico_main.app, ["status"], catch_exceptions=False)
        assert result.exit_code == 0
        # Status should print (not raise FileNotFoundError, etc)
        output = result.output
        assert "src_folder" in output or "Status: " in output
    finally:
        os.chdir(prev_cwd)