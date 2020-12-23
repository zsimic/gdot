import os

import runez


__version__ = "0.0.0"
GDOT_GIT_STORE = "~/.config/gdot-git-store"


class GDot:
    """Handling of the gdot store"""

    gdot_store = runez.resolved_path(GDOT_GIT_STORE)
    current_user = os.environ.get("USER")

    @classmethod
    def formatted(cls, text):
        if text:
            text = text.format(userid=cls.current_user or "USERID", gdot_store=runez.short(cls.gdot_store))

        return text
