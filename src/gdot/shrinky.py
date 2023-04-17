#!/usr/bin/env python3
"""
Standalone script used to render PS1 parts and shortened folder names for tmux window names and shell prompts.
Must work fast, with system python, std libs only
"""

import os
import re
import sys
from pathlib import Path


def run_program(*args: str):
    import subprocess  # nosec B404

    p = subprocess.run(args, stdout=subprocess.PIPE, shell=False)  # nosec B603
    if p.returncode == 0 and p.stdout:
        return p.stdout.decode("utf-8").strip()


def get_path(path):
    if path == "~":
        return Path(os.path.expanduser("~"))

    if path:
        if not isinstance(path, Path):
            if path.startswith('"') and path.endswith('"'):
                path = path.strip('"')

            if path:
                path = Path(path)

    return path


def scm_root(folder: Path):
    if (folder / ".git").is_dir():
        return folder

    folder = folder.parent
    if len(folder.parts) > 1:
        return scm_root(folder)


def capped_text(text: str, max_size: int):
    if max_size and text and len(text) > max_size:
        # netflix-grpc-client-𓈓
        # netflix-grpc-client-gen-py
        text = "𓈓%s" % text[-max_size:]

    return text


class ColorBit:
    def __init__(self, name, open_marker, close_marker, wrapper_fmt=None):
        self.name = name
        self.open_marker = open_marker
        self.close_marker = close_marker
        self.wrapper_fmt = wrapper_fmt

    def __repr__(self):  # pragma: no cover, debugger only
        return self.__call__(self.name)

    def wrapped(self, marker):
        if self.wrapper_fmt:
            marker = self.wrapper_fmt % marker

        return marker

    def __call__(self, text):
        open_marker = self.wrapped(self.open_marker)
        close_marker = self.wrapped(self.close_marker)
        return f"{open_marker}{text}{close_marker}"


class ColorSet:
    available = ("bold", "blue", "green", "yellow", "red", "cyan")  # magenta

    def __init__(self, name, bits):
        self.name = name
        self.bits = bits  # type: dict[str, ColorBit]
        self.bold = self.bits["bold"]
        self.blue = self.bits["blue"]
        self.green = self.bits["green"]
        self.yellow = self.bits["yellow"]
        self.red = self.bits["red"]
        self.cyan = self.bits["cyan"]

    @classmethod
    def tty_color_set(cls, name="tty-colors"):
        codes = dict(bold=1, blue=34, green=32, yellow=33, red=31, cyan=36)
        code_format = "\x1b[%sm"
        clear = code_format % ""
        wrapper_fmt = None
        if "ps1" in name:
            wrapper_fmt = "\\[%s\\]"

        codes = {k: ColorBit(k, code_format % v, clear, wrapper_fmt=wrapper_fmt) for k, v in codes.items()}
        return cls(name, codes)

    @classmethod
    def ps1_for_shell(cls, shell):
        func = getattr(cls, "%s_ps1_color_set" % shell, None)
        if func:
            return func()

    @classmethod
    def bash_ps1_color_set(cls):
        return cls.tty_color_set(name="bash-ps1-colors")

    @classmethod
    def zsh_ps1_color_set(cls):
        bits = {}
        for name in cls.available:
            cb = ColorBit(name, "%B", "%b") if name == "bold" else ColorBit(name, "%%F{%s}" % name, "%f")
            bits[cb.name] = cb

        return cls("zsh-ps1-colors", bits)

    def __repr__(self):  # pragma: no cover, debugger only
        return self.name


TTYC = ColorSet.tty_color_set()


def shortened_path(prefix, parts, max_parts=6):
    yield prefix
    if len(parts) > max_parts:
        yield "𓈓"
        parts = parts[-max_parts:]

    pivot = len(parts) - 2
    for i, part in enumerate(parts):
        if i < pivot:
            yield part[0]

        else:
            yield part


def folder_parts(folder: Path):
    try:
        return "~", folder.relative_to(get_path("~")).parts

    except ValueError:
        return "", folder.parts[1:]


class CommandRenderer:

    flags = {}


class PathCleaner(CommandRenderer):

    flags = dict(p="path")
    path = ""

    def cmd_clean_path(self):
        path = self.path or os.environ.get("PATH")
        seen = set()
        for folder in path.split(os.pathsep):
            folder = get_path(folder)
            if folder not in seen and folder.is_dir():
                yield str(folder)

            seen.add(folder)


class Ps1Renderer(CommandRenderer):

    dockerenv = "/.dockerenv"
    example = "ps1 -szsh -ozsimic,zoran -p.. -ufoo"
    flags = dict(s="shell", o="owner", u="user", x="exit_code", p="pwd", v="venv", w="window")

    exit_code = "0"
    owner = ""
    pwd = ""  # nosec B105
    shell = ""
    window = ""
    user = ""
    venv = ""

    def cmd_ps1(self):
        """
        PS1 minimalistic prompt
        """
        colors = ColorSet.ps1_for_shell(self.shell)
        if not colors:
            CommandParser.fail("Shell '%s' not supported" % self.shell)

        if os.path.exists(self.dockerenv):
            yield "🐳 "

        elif self.user == "root":
            yield "❕ "

        if self.venv:
            venv = get_path(self.venv)
            activate = venv / "bin/activate"
            python = venv / "bin/python"
            py_version = run_program(str(python), "--version") if python.exists() else None
            if py_version:
                m = re.search(r"(\d+\.\d+)", py_version)
                if m:
                    py_version = m.group(1)

            venv_name = None
            if activate.exists():
                regex = re.compile(r"""^\s*PS1="\(([\w-]+).+""")
                for line in activate.read_text().splitlines():
                    m = regex.match(line)
                    if m:
                        venv_name = m.group(1)

            if not venv_name:
                if venv.name == ".venv":
                    venv = venv.parent

                venv_name = venv.name

            venv_name = capped_text(venv_name, 24)
            py_version = capped_text(py_version, 5)
            yield "(%s %s) " % (colors.cyan(venv_name), colors.blue(py_version))

        if self.owner and self.user != "root":
            owners = self.owner.split(",")
            if self.user not in owners:
                yield "%s@" % colors.blue(self.user)

        if self.pwd:
            folder = get_path(self.pwd)
            prefix, parts = folder_parts(folder)
            yield colors.yellow("/".join(shortened_path(prefix, parts)))

        color = colors.green if self.exit_code == "0" else colors.red
        char = color(" #" if self.user == "root" else ":")
        yield "%s " % char


class TmuxBranchSpec:
    def __init__(self, spec):
        self.spec = spec
        visual, _, branches = spec.partition(":")
        self.icon = spec[0] if spec else None
        self.color = spec[1:] if spec else None
        self.branches = branches.split(",") if branches else None


class TmuxBranchSpecs:

    def __init__(self, specs):
        specs = specs or TmuxRenderer.branch_spec
        self.specs = specs.split("+")
        self.default = None
        self.by_branch = {}
        for spec in self.specs:
            spec = TmuxBranchSpec(spec)
            if spec.branches:
                for branch in spec.branches:
                    self.by_branch[branch] = spec

            else:
                self.default = spec

    def get_spec(self, branch):
        return self.by_branch.get(branch, self.default)


class TmuxRenderer(CommandRenderer):

    # Other icons: 🔀🧐🚨🚧📌🔧📄💡🍻🏷️💫🩹🎨
    branch_spec = "📌yellow+✨blue:master,main+🧐green:release,publish"
    path = ""
    window = ""
    flags = dict(b="branch_spec", p="path", w="window")

    @staticmethod
    def tmux_colored(text, fg: str, max_size: int):
        text = capped_text(text, max_size)
        if fg:
            text = "#[fg=%s]%s#[default]" % (fg, text)

        return text

    def rendered_branch(self, folder):
        if folder:
            branch_name = run_program("git", "-C", folder, "branch", "--no-color", "--show-current")
            if branch_name:
                specs = TmuxBranchSpecs(self.branch_spec)
                spec = specs.get_spec(branch_name)
                if spec:
                    return "%s%s" % (self.tmux_colored(branch_name, spec.color, 20), spec.icon)

    @staticmethod
    def uptime_bits(text):
        for bit in text.split(","):
            bit = bit.strip()
            if bit:
                if "user" in bit or "session" in bit or "load" in bit:
                    return

                if ":" in bit:
                    h, _, m = bit.partition(":")
                    yield "%sh" % h
                    yield "%sm" % m
                    continue

                n, _, unit = bit.partition(" ")
                unit = unit.strip()
                if n and unit:
                    bit = "%s%s" % (n, unit[0])

                yield bit

    def rendered_uptime(self):
        """
        12:41  up 1 day, 46 mins, 1 user, load averages: 4.79 3.38 2.84
        4:12pm  up 23 days,  2:03, 3 sessions , load average: 0.00, 0.00, 0.00
        4:13pm  up  7:00, 1 session , load average: 0.00, 0.00, 0.00
        """
        stdout = run_program("uptime")
        if stdout and "up" in stdout:
            i = stdout.index("up")
            stdout = stdout[i + 2:].strip()
            if stdout:
                up = list(self.uptime_bits(stdout))[:2]
                if up:
                    return "%s🔌" % self.tmux_colored(" ".join(up), "dim", 10)  # 🕤⏳🪫🔋🔌

    def cmd_tmux_status(self):
        """
        Status for tmux status-right part

        Example:
          set -g status-right '#(/usr/bin/python3 shrinky.py tmux_status -p"#{pane_current_path}")'
        """
        folder = get_path(self.path)
        yield self.rendered_branch(scm_root(folder))
        yield self.rendered_uptime()

    def cmd_tmux_short(self):
        """
        Short name to show for a given window

        Example:
          setw -g automatic-rename-format '#(/usr/bin/python3 shrinky.py tmux_short -b📌yellow+✨blue,master,main -p"#{pane_current_path}")'
        """
        folder = get_path(self.path)
        if folder == get_path("~"):
            yield "~"
            return

        root = scm_root(folder)
        if root and folder != root:
            folder = "%s/%s" % (root.name, folder.relative_to(root).name)

        else:
            folder = folder.name

        yield capped_text(folder, max_size=20)


class CommandDef:
    def __init__(self, base_cls, name, delimiter):
        self.name = name
        self.base_cls = base_cls
        self.delimiter = delimiter

    def __repr__(self):  # pragma: no cover, debugger only
        return self.name

    def get_func(self, instance=None):
        func = getattr(instance or self.base_cls, "cmd_%s" % self.name)
        return func

    def get_doc(self):
        func = self.get_func()
        doc = func.__doc__ or "?"
        return doc

    def summary(self):
        return self.get_doc().strip().splitlines()[0]

    def run_with_args(self, args):
        instance = self.base_cls()
        for arg in args:
            if not arg or len(arg) <= 1 or not arg.startswith("-"):
                CommandParser.fail("Unrecognized argument '%s'" % arg)

            key = arg[1]
            value = arg[2:]
            flag = self.base_cls.flags.get(key)
            if not flag:
                CommandParser.fail("Unknown flag '%s'" % key)

            setattr(instance, flag, value)

        func = self.get_func(instance=instance)
        bits = list(func())
        print(self.delimiter.join(x for x in bits if x))

    def show_help(self):
        from textwrap import dedent

        doc = self.get_doc()
        doc = dedent(doc).strip()
        print("%s\n" % doc)
        sys.exit(0)


class CommandParser:
    def __init__(self):
        self.available_commands = {}

    def add_command(self, cmd, delimiter=""):
        for k in dir(cmd):
            if k.startswith("cmd_"):
                name = k[4:]
                cmd_def = CommandDef(cmd, name, delimiter)
                self.available_commands[name] = cmd_def

    @staticmethod
    def warn(msg):
        if msg:
            print(msg, file=sys.stderr)

    @staticmethod
    def fail(msg, exit_code=1):
        CommandParser.warn(msg)
        sys.exit(exit_code)

    def get_command(self, name, fatal=True):
        cmd = self.available_commands.get(name)
        if cmd is None and fatal:
            self.fail("Unknown command '%s'" % name)

        return cmd

    def show_help(self, msg=None, exit_code=0):
        self.warn(msg)
        print("Usage: COMMAND [ARGS]...")
        print(__doc__)
        print("\nCommands:")
        for name, cmd in sorted(self.available_commands.items()):
            print("  %s%s" % (TTYC.bold("%-18s" % name), cmd.summary()))

        if exit_code is not None:
            sys.exit(exit_code)

    def run_args(self, args):
        if not args:
            self.show_help("No command provided", exit_code=1)

        cmd = args[0]
        args = args[1:]
        if cmd == "--help":
            self.show_help()

        cmd = self.get_command(cmd)
        if "--help" in args:
            cmd.show_help()

        try:
            cmd.run_with_args(args)

        except Exception as e:
            self.fail("'%s()' crashed: %s" % (cmd.name, e))


def main(args=None):
    parser = CommandParser()
    parser.add_command(PathCleaner, delimiter=os.pathsep)
    parser.add_command(Ps1Renderer)
    parser.add_command(TmuxRenderer, delimiter="┆")
    parser.run_args(args or sys.argv[1:])


if __name__ == "__main__":  # pragma: no cover
    main()
