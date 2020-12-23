import os
import sys

import runez
from runez.render import PrettyTable


__version__ = "0.0.1"
GDOT_GIT_STORE = "~/.config/gdot-git-store"
ISSUES_URL = "https://github.com/codrsquad/gdot/issues"


ISSUE_TEMPLATE = """
Please {report} this issue to us on %s
Here's a snippet you can include in your report to help us triage:

{diagnostics}
""" % ISSUES_URL


def complain(message):
    if message:
        sys.stderr.write(message)
        if not message.endswith("\n"):
            sys.stderr.write("\n")


def env_var_value(*names, **kwargs):
    for name in names:
        value = os.environ.get(name)
        if value:
            return value

    return kwargs.get("default")


class GDotOfficer:
    """Handling of the gdot store"""

    def __init__(self):
        if os.geteuid() == 0:
            complain("%s was not designed to run as %s\n\n" % (runez.blue("gdot"), runez.red("root")))
            complain("Please %s if you see a use-case for that on %s\n\n" % (runez.yellow("let us know"), ISSUES_URL))
            sys.exit(1)

        self.userid = os.environ.get("USER")
        self.store_path = env_var_value("GDOT_GIT_STORE", default=GDOT_GIT_STORE)
        self.git_store = runez.resolved_path(self.store_path)
        if not self.userid:
            self.abort("Could not determine userid")

    def get_diagnostics(self, border="colon"):
        table = PrettyTable(2, border=border)
        table.header[0].align = "right"
        table.header[1].style = "bold"
        vid = "v%s" % __version__
        if self.store_path != GDOT_GIT_STORE:
            vid += runez.dim(" (%s)" % self.store_path)

        table.add_row("gdot", vid)
        table.add_row("args", runez.log.spec.argv)
        python_info = ".".join(str(n) for n in sys.version_info[:3])
        prefix = getattr(sys, "real_prefix", getattr(sys, "base_prefix", sys.prefix))
        if prefix:
            python_info += runez.dim(" (%s)" % runez.short(prefix))

        table.add_row("python", python_info)
        if sys.prefix != prefix:
            table.add_row("venv", runez.short(sys.prefix))

        table.add_row("platform", runez.run("uname", "-mprs").output)
        table.add_row("shell", runez.short(env_var_info("SHELL")))
        table.add_row("terminal", runez.short(env_var_info("TERM_PROGRAM", "LC_TERMINAL")))
        table.add_row("TERM", runez.short(env_var_info("TERM")))
        return str(table)

    def abort(self, message):
        complain(message)
        instructions = ISSUE_TEMPLATE.format(report=runez.red("report"), diagnostics=self.get_diagnostics())
        complain(instructions)
        sys.exit(1)


def env_var_info(*names):
    value = env_var_value(*names)
    if not value:
        value = runez.dim("-unknown-")

    return value
