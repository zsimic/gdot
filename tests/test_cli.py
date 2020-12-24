import subprocess
import sys

import runez
from mock import patch

from gdot import GDotX


def test_attach(cli):
    GDotX.gv.userid = None
    cli.run("attach", "url")
    assert cli.failed
    assert "Could not determine user" in cli.logged
    GDotX.gv.userid = "tester"


def test_main():
    r = subprocess.check_output([sys.executable, "-mgdot", "--help"])  # Exercise __main__.py
    r = runez.decode(r)
    assert "For more info see" in r


def test_no_root(cli):
    with patch("os.geteuid", return_value=0):
        cli.run("diagnostics", "--help")
        assert cli.failed
        assert "gdot was not designed to run as root" in cli.logged


def test_sanity_check(cli):
    cli.expect_success("--version")
    assert cli.succeeded
    assert "gdot" in cli.logged

    cli.run("git", "--help")
    assert cli.succeeded
    assert GDotX.gv.default_store in cli.logged


def test_secondary_commands(cli):
    cli.run("diagnostics")
    assert cli.succeeded
    assert "terminal : -unknown-" in cli.logged
