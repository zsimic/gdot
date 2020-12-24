import os
import sys

import runez
from runez import cached_property, chill_property
from runez.render import PrettyTable


__version__ = "0.0.1"

ISSUE_TEMPLATE = """
Please {report} this issue to us on {issues_url}
Here's a snippet you can include in your report to help us triage:

{diagnostics}
"""


def complain(message):
    if message:
        sys.stderr.write(message)
        if not message.endswith("\n"):
            sys.stderr.write("\n")


def env(name, default=None):
    value = os.environ.get(name)
    if value:
        return value

    return default


def shell(*script):
    r = runez.run(*script, fatal=False, logger=None)
    if r.succeeded:
        return r.output


class EnvirnonmentInfo:
    """Various information about the current environment"""

    @chill_property
    def machine_hardware(self):
        yield shell("uname", "-m")

    @chill_property
    def os_name(self):
        yield shell("uname", "-s")

    @chill_property
    def os_release(self):
        yield shell("uname", "-r")

    @cached_property
    def platform_string(self):
        return runez.joined(self.os_name, self.os_release, self.machine_hardware, self.processor_architecure)

    @chill_property
    def processor_architecure(self):
        yield shell("uname", "-p")

    @cached_property
    def python_info(self):
        text = self.python_version
        if self.python_prefix:
            text += runez.dim(" (%s)" % runez.short(self.python_prefix))

        return text

    @cached_property
    def python_prefix(self):
        return getattr(sys, "real_prefix", getattr(sys, "base_prefix", sys.prefix))

    @cached_property
    def python_version(self):
        return ".".join(str(n) for n in sys.version_info[:3])

    @chill_property
    def shell(self):
        yield env("SHELL")

    @chill_property
    def term(self):
        yield env("TERM")

    @chill_property
    def term_program(self):
        yield env("TERM_PROGRAM")
        yield env("LC_TERMINAL")

    @cached_property
    def venv(self):
        if sys.prefix != self.python_prefix:
            return sys.prefix


class GDEnv:
    """Environment related stuff"""

    default_store = "~/.config/gdot-git-store"
    issues_url = "https://github.com/codrsquad/gdot/issues"

    @cached_property
    def help_keywords(self):
        return dict(userid=self.userid or "USERID", default_store=self.default_store, issues_url=self.issues_url)

    @chill_property
    def userid(self):
        yield env("USER")

    @cached_property
    def environment_info(self):
        return EnvirnonmentInfo()

    def formatted(self, text, **keywords):
        if text:
            text = text.format(**self.help_keywords, **keywords)

        return text


class GDotX:
    """Handling of the gdot store"""

    gv = GDEnv()
    store_path = None  # type: str # Store path as configured
    git_store = None  # type: str # Full absolute path to git store

    def __init__(self):
        self.set_path(env("GDOT_GIT_STORE", default=self.gv.default_store))

    def set_path(self, path):
        self.store_path = path
        self.git_store = runez.resolved_path(path)

    def attach(self, url):
        pass

    @cached_property
    def gdot_info(self):
        vid = "v%s" % __version__
        if self.store_path != GDEnv.default_store:
            vid += runez.dim(" (%s)" % self.store_path)

        return vid

    def get_diagnostics(self, border="colon"):
        info = self.gv.environment_info
        table = PrettyTable(2, border=border)
        table.header[0].align = "right"
        table.header[1].style = "bold"
        add_row(table, "gdot", self.gdot_info)
        add_row(table, "args", runez.log.spec.argv)
        add_row(table, "userid", self.gv.userid)
        add_row(table, "python", info.python_info)
        add_row(table, "venv", info.venv)
        add_row(table, "platform", info.platform_string)
        add_row(table, "shell", info.shell)
        add_row(table, "terminal", info.term_program)
        add_row(table, "TERM", info.term)
        return str(table)

    def abort(self, message):
        complain(message)
        instructions = ISSUE_TEMPLATE.format(report=runez.red("report"), diagnostics=self.get_diagnostics(), issues_url=GDEnv.issues_url)
        complain(instructions)
        sys.exit(1)


def add_row(table, *args):
    default = runez.dim("-unknown-")
    args = [runez.short(x or default) for x in args]
    table.add_row(*args)
