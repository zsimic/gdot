# -*- encoding: utf-8 -*-

import os
import re
import sys

import runez
from runez import cached_property, chill_property
from runez.render import PrettyTable


ISSUE_TEMPLATE = """
Please {report} this issue to us on {issues_url}
Here's a snippet you can include in your report to help us triage:

{diagnostics}
"""
KNOWN_TERMS = r"""
alacritty
(gnome|xfce.)-term\w*
(g|yak)uake
konsole
rxvt
termin(ator|ology|al\.app)
til(da|lix)
[eiwxz]term
"""


def shell(*script):
    """str: Output from given shell script"""
    r = runez.run(*script, fatal=False, logger=None)
    if r.succeeded:
        return r.output


class MachineInfo:
    """Machine info for reporting diagnostics, this info should never change so can be cached"""

    def __repr__(self):
        return runez.joined(self.os_name, self.os_release, self.hardware, self.arch)

    @cached_property
    def hardware(self):
        return shell("uname", "-m")

    @cached_property
    def os_name(self):
        return shell("uname", "-s")

    @cached_property
    def os_release(self):
        return shell("uname", "-r")

    @cached_property
    def arch(self):
        return shell("uname", "-p")


class SystemInfo:
    """General system information"""

    @cached_property
    def machine_info(self):
        return MachineInfo()

    @cached_property
    def current_process(self):
        return runez.ps_info(os.getpid())

    @cached_property
    def parent_process(self):
        return runez.ps_info(os.getppid())

    @cached_property
    def process_tree(self):
        """str: Short representation of process tree where gdot is running (shows invoking shell)"""
        ptree = []
        p = self.parent_process
        while p:
            if p.cmd_basename:
                if "tmux" in p.cmd_basename:
                    tmuxp = list(_tmux_process_tree())
                    if tmuxp:
                        return ptree + tmuxp

            ptree.append(p)
            p = p.parent

        return ptree

    @cached_property
    def base_prefix(self):
        return getattr(sys, "real_prefix", getattr(sys, "base_prefix", sys.prefix))

    @cached_property
    def python_venv(self):
        if sys.prefix != self.base_prefix:
            return sys.prefix

    @cached_property
    def python_version(self):
        impl = getattr(sys, "implementation", "")
        if impl:
            impl = getattr(impl, "name", "")

        if impl:
            impl = "%s " % impl

        return "%s%s" % (impl, sys.version)

    @cached_property
    def term_program(self):
        for k in ("LC_TERMINAL", "TERM_PROGRAM"):
            tp = os.environ.get(k)
            if tp:
                version = os.environ.get(k + "_VERSION")
                if version:
                    tp += runez.dim(" v%s" % version)

                return tp

        regex = "|".join(KNOWN_TERMS.strip().splitlines())
        regex = re.compile(r"\b(%s)" % regex, re.IGNORECASE)
        for p in self.process_tree:
            if p.cmd:
                m = regex.search(p.cmd)
                if m:
                    return "%s %s" % (m.group(1), runez.dim("(%s)" % p.cmd))


class BaseFolder:
    def __init__(self, default):
        path = runez.log.dev_folder(os.path.basename(default))
        if not path:
            path = os.environ.get("GDOT_GIT_STORE")

        if not path:
            path = default

        self.path = runez.resolved_path(path)

    def full_path(self, *relative_path):
        return os.path.join(self.path, *relative_path)


class GDEnvBase:
    """Environment related stuff"""

    default_store = "~/.config/gdot-git-store"
    issues_url = "https://github.com/codrsquad/gdot/issues"

    user_home = None  # type: str # User ~ folder (unless running in test mode)
    store_home = None  # type: str # Store base folder

    def home_path(self, path):
        pass

    def cache_path(self):
        pass

    @cached_property
    def base_folder(self):
        return BaseFolder(self.default_store)

    @cached_property
    def gdot_info(self):
        vid = "v%s" % runez.get_version(__package__)
        if self.base_folder.path != GDEnv.default_store:
            vid += runez.dim(" (%s)" % self.base_folder.path)

        return vid

    @cached_property
    def help_keywords(self):
        return dict(userid=self.userid or "USERID", default_store=self.default_store, issues_url=self.issues_url)

    @chill_property
    def userid(self):
        yield os.environ.get("USER")
        yield self.sys_info.current_process.userid

    @cached_property
    def sys_info(self):
        return SystemInfo()

    def _diagnostics(self, verbose):
        info = self.sys_info
        yield "gdot", self.gdot_info
        yield "userid", self.userid
        yield "args", runez.log.spec.argv
        yield "python version", info.python_version
        yield "python venv", info.python_venv
        yield "python exe", info.base_prefix
        yield "platform", info.machine_info
        delim = "/" if runez.PY2 else "⚡"
        yield "invoked via", runez.joined([p.cmd_basename for p in info.process_tree], keep_empty=False, delimiter=" %s " % delim)
        yield "terminal", info.term_program
        yield "TERM", os.environ.get("TERM")

        if verbose:
            yield runez.yellow("sys attributes"), runez.yellow("----")
            for k in sorted(dir(sys)):
                if k.startswith("_") or not hasattr(sys, k):
                    continue

                v = getattr(sys, k)
                if v and not callable(v):
                    yield k, v

            yield runez.yellow("Environment variables"), runez.yellow("----")
            for k in sorted(os.environ):
                yield k, os.environ.get(k)

    def diagnostics(self, verbose=False, border="colon"):
        table = PrettyTable(2, border=border)
        table.header[0].align = "right"
        table.header[1].style = "bold"
        term_width = runez.terminal_width()
        rows = list()
        col1 = 0
        col2 = 0
        rows = []
        for row in self._diagnostics(verbose):
            row = [runez.stringified(c, none=self._unknown) for c in row]
            if len(row) == 2 and row[1]:
                col1 = max(col1, len(row[0]))
                col2 = max(col2, len(row[1]))

            rows.append(row)

        size_col2 = term_width - col1 - 5
        for row in rows:
            if len(row) == 2 and row[1]:
                row[1] = runez.short(row[1], size=size_col2)

        table.add_rows(*rows)
        return str(table)

    @cached_property
    def _unknown(self):
        return runez.dim("-unknown-")

    def formatted(self, text, **keywords):
        if text:
            keywords.update(self.help_keywords)
            text = text.format(**keywords)

        return text

    @staticmethod
    def complain(message):
        if message:
            sys.stderr.write(message)
            if not message.endswith("\n"):
                sys.stderr.write("\n")

    def abort(self, message):
        self.complain(message)
        instructions = ISSUE_TEMPLATE.format(report=runez.red("report"), diagnostics=self.diagnostics(), issues_url=GDEnv.issues_url)
        self.complain(instructions)
        sys.exit(1)


def _tmux_process_tree():
    p = runez.to_int(shell("tmux", "display-message", "-p", "#{client_pid}"))
    if p:
        p = runez.ps_info(p)
        while p:
            yield p
            p = p.parent


GDEnv = GDEnvBase()
