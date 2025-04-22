import logging
import os
import sys
from pathlib import Path
import shutil

from aico.utils import list_dir
from microcore import ui

def test():
    # get temp dir for tests on FS
    tests_root = Path(__file__).parent.parent
    temp_dir= tests_root / 'temp'
    shutil.rmtree(temp_dir, ignore_errors=True)
    temp_dir.mkdir(exist_ok=True)
    (temp_dir / 'dir1').mkdir()
    (temp_dir / 'dir2').mkdir()
    (temp_dir / 'dir2' / 'dir1').mkdir()
    (temp_dir / 'dir13').mkdir()
    (temp_dir / 'prefixed_dir1').mkdir()
    (temp_dir / 'empty_dir').mkdir()
    # touch files
    (temp_dir / 'dir1' / 'file1A.txt').touch()
    (temp_dir / 'dir1' / 'file2B.txt').touch()
    (temp_dir / 'dir2' / 'file3A.txt').touch()
    (temp_dir / 'dir2' / 'file4B.txt').touch()
    (temp_dir / 'dir2' / 'dir1' / 'file4B.txt').touch()
    (temp_dir / 'dir13' / 'file5A.txt').touch()
    (temp_dir / 'prefixed_dir1' / 'file6A.txt').touch()
    ignore_root_d1 = ['dir13/file5A.txt', 'dir2/file3A.txt', 'dir2/file4B.txt', 'prefixed_dir1/file6A.txt']
    assert list_dir(temp_dir, ignore=['dir1']) == ignore_root_d1
    assert list_dir(temp_dir, ignore=['dir1/*']) == ignore_root_d1
    assert list_dir(temp_dir, ignore=['file*A*']) == ['dir1/file2B.txt', 'dir2/dir1/file4B.txt', 'dir2/file4B.txt']
    assert list_dir(temp_dir, ignore=['file*A*', 'dir1']) == ['dir2/file4B.txt']
    assert len(list_dir(temp_dir)) == 7
    assert len(list_dir(temp_dir, ignore=['file*'])) == 0
    assert len(list_dir(temp_dir, ignore=['file'])) == 7


    shutil.rmtree(temp_dir, ignore_errors=True)
