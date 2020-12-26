import os

import runez
from runez.conftest import cli

from gdot import GDEnv
from gdot.commands import main


def full_path(*relative_path):
    pwd = os.getcwd()
    assert "private" in pwd or "tmp" in pwd, "Test ran in non-temp folder"
    relative = os.path.join(*relative_path)
    assert not os.path.isabs(relative), "Abs path not allowed: %s" % relative
    return os.path.join(pwd, relative)


cli.default_main = main
GDEnv.userid = "tester"
GDEnv.base_folder.path = runez.UNSET
GDEnv.base_folder.full_path = full_path
