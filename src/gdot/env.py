# -*- encoding: utf-8 -*-

import os
import sys

import runez
from runez import cached_property
from runez.pyenv import PythonDepot
from runez.render import PrettyTable


ISSUE_TEMPLATE = """
Please {report} this issue to us on {issues_url}
Here's a snippet you can include in your report to help us triage:

{diagnostics}
"""


class BaseFolder:
    def __init__(self, default):
        path = runez.DEV.venv_path(os.path.basename(default))
        if not path:
            path = os.environ.get("GDOT_GIT_STORE")

        if not path:
            path = default

        self.path = runez.resolved_path(path)

    def __repr__(self):
        return runez.short(self.path)

    def full_path(self, *relative_path):
        return os.path.join(self.path, *relative_path)


class GDEnvBase:
    """Environment related stuff"""

    default_store = "~/.config/gdot-git-store"
    issues_url = "https://github.com/zsimic/gdot/issues"

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
    def help_keywords(self):
        return dict(userid=runez.SYS_INFO.userid or "USERID", default_store=self.default_store, issues_url=self.issues_url)

    def _diagnostics(self):
        yield "base", self.base_folder
        yield "invoker python", PythonDepot(use_path=False).invoker.representation()

    def diagnostics(self):
        return PrettyTable.two_column_diagnostics(self._diagnostics)

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


GDEnv = GDEnvBase()
