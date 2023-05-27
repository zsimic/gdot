import os
import sys
from pathlib import Path

import runez

import gdot.shrinky
from gdot.shrinky import main


def test_clean_path(cli):
    runez.touch("foo/bar/readme.txt")
    cli.run("clean_path -pfoo:baz:foo/bar:baz2:/foo/bar/baz", main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "foo:foo/bar\n"


def test_colors():
    x = gdot.shrinky.ColorSet.zsh_ps1_color_set()
    assert str(x) == "zsh-ps1-colors"
    assert str(x.bold) == "%Bbold%b"


def test_help(cli):
    cli.run("--help", main=main)
    assert cli.succeeded
    assert "Usage:" in cli.logged.stderr

    cli.run("tmux_status --help", main=main)
    assert cli.succeeded
    assert "Example:\n  set -g status-right" in cli.logged.stderr


def test_invalid(cli, monkeypatch):
    cli.run("", main=main)
    assert cli.failed
    assert "No command provided" in cli.logged.stderr

    cli.run("foo", main=main)
    assert cli.failed
    assert cli.logged.stderr.contents() == "Unknown command 'foo'\n"
    assert not cli.logged.stdout

    cli.run("ps1 foo", main=main)
    assert cli.failed
    assert cli.logged.stderr.contents() == "Unrecognized argument 'foo'\n"

    cli.run("ps1", main=main)
    assert cli.failed
    assert cli.logged.stderr.contents() == "Shell '' not supported\n"

    cli.run("ps1 -sfoo", main=main)
    assert cli.failed
    assert cli.logged.stderr.contents() == "Shell 'foo' not supported\n"

    cli.run("ps1 -z5", main=main)
    assert cli.failed
    assert cli.logged.stderr.contents() == "Unknown flag 'z'\n"

    # Simple message on stderr on crash
    monkeypatch.setattr(gdot.shrinky, "folder_parts", lambda *_: None)
    cli.run("-v ps1 -szsh -pfoo/bar", main=main)
    assert cli.failed
    assert "'ps1()' crashed: cannot unpack non-iterable NoneType object\n" in cli.logged.stderr
    assert "in cmd_ps1" in cli.logged.stderr


def test_deep_ps1(cli, monkeypatch):
    sample = "sample/some/very/deep/folder/with/way/too/many/characters/tests"
    runez.touch("%s/.git" % sample)
    full_path = os.path.abspath("%s/foo/bar/baz/even/more/tests" % sample)
    venv = "%s/.venv" % full_path
    runez.write("%s/bin/activate" % venv, '\nPS1="(some-very-long-venv-prompt) ${PS1:-}"')
    cli.run('ps1 -szsh -p"%s" -v"%s/.venv"' % (full_path, full_path), main=main)
    assert cli.succeeded
    expected = "(%F{cyan}𓈓me-very-long-venv-prompt%f %F{blue}None%f) %F{yellow}/𓈓/f/b/b/e/more/tests%f%F{green}:%f \n"
    assert cli.logged.stdout.contents() == expected

    # Simulate docker
    monkeypatch.setattr(gdot.shrinky.Ps1Renderer, "dockerenv", ".")
    cli.run("ps1 -szsh", main=main)
    assert cli
    assert cli.logged.stdout.contents() == "🐳 %F{green}:%f \n"


def test_get_path():
    cwd = Path(".")
    assert gdot.shrinky.get_path(None) == cwd
    assert gdot.shrinky.get_path("") == cwd
    assert gdot.shrinky.get_path(".") == cwd
    assert gdot.shrinky.get_path('"."') == cwd
    assert gdot.shrinky.get_path(Path(".")) == cwd

    user_dir = Path(os.path.expanduser("~"))
    assert gdot.shrinky.get_path("~") == user_dir
    assert gdot.shrinky.get_path('"~"') == user_dir


def test_ps1(cli):
    cli.run("ps1 -szsh -uroot -x0 -p/tmp/foo/bar/baz -v", main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "❕ %F{yellow}/t/f/bar/baz%f%F{green} #%f \n"

    # User shown when not matching stated owner
    cli.run("ps1 -szsh -uuser1 -ouser2,user3 -x1", main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "%F{blue}user1%f@%F{red}:%f \n"

    # This test's own venv
    venv_path = os.path.dirname(os.path.dirname(sys.executable))
    py_version = ".".join(str(x) for x in sys.version_info[:2])
    cli.run("ps1", "-szsh", "-x1", "-v%s" % venv_path, main=main)
    assert cli.succeeded
    output = cli.logged.stdout.contents()
    assert py_version in output

    # A fictional venv
    cli.run("ps1", "-szsh", "-vfoo/bar/.venv", main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "(%F{cyan}bar%f %F{blue}None%f) %F{green}:%f \n"

    # Minimal args
    cli.run("ps1 -sbash", main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "\\[\x1b[32m\\]:\\[\x1b[m\\] \n"


def test_tmux(cli, monkeypatch):
    monkeypatch.setattr(gdot.shrinky.Logger, "log_location", "test.log")
    cli.run("-v tmux_short -p%s" % os.environ.get("HOME"), main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "~\n"

    project_path = runez.DEV.project_path("src/gdot")
    cli.run("tmux_short -p%s" % project_path, main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "gdot/gdot\n"

    cli.run("tmux_short -p~/dev/foo/bar", main=main)
    assert cli.succeeded
    assert cli.logged.stdout.contents() == "bar\n"

    cli.run("tmux_status -p%s" % project_path, main=main)
    assert cli.succeeded
    assert "#[default]🔌" in cli.logged.stdout
