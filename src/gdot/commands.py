"""
\b
To get started, attach to a git repo that will be used to track your files, for example:
\b
    gdot attach gitlab:{userid}
\b
For more info see http://gdot.dev
"""

import os
import sys

import click
import runez

from gdot import GDOT_GIT_STORE, GDotOfficer


GDOT = None  # type: GDotOfficer


def not_implemented():
    caller = runez.system.find_caller_frame()
    sys.exit("gdot %s is not yet implemented" % runez.red(caller.f_code.co_name))


@runez.click.group(epilog=__doc__)
@runez.click.version()
@runez.click.debug()
@runez.click.dryrun()
@runez.click.color()
def main(debug):
    """Git my dotfiles"""
    global GDOT
    runez.log.setup(debug=debug, greetings=":: {argv}")
    GDOT = GDotOfficer()


@main.command()
@click.argument("file")
def add(file):
    """
    Add a file or folder to track via gdot

    Example:
        gdot add .bashrc
        gdot add ~/.config/htop/
    """
    not_implemented()


@main.command()
@click.argument("url")
def attach(url):
    """
    Attach with remote git url

    Examples:
        gdot attach github:{userid}
        gdot attach git@github.com:{userid}/dotfiles.git
    \b
    Accepted URL formats:
    - handy shortcuts such as 'github:{userid}' or 'gitlab:{userid}'
    - full url to a git repo such as 'git@github.com:{userid}/dotfiles.git'
    """
    print(url)


@main.command()
def detach():
    """
    Detach from remote
    All local files will remain as-is,
    but gdot won't consider them linked with any remote
    """
    not_implemented()


@main.command()
def diff():
    """Show what's changed since last pull/push/sync"""
    not_implemented()


@main.command()
def git():
    """
    Run a git command on the dotfiles repo

    This is the same as running:
        cd {store_path}
        git ...
    """
    not_implemented()


@main.command()
def list():
    """List currently tracked files/folders"""
    not_implemented()


@main.command()
def neofetch():
    """Convenience neofetch clone, but *much* faster"""
    not_implemented()


@main.command()
def pull():
    """Pull state from remote git repo"""
    not_implemented()


@main.command()
def push():
    """Push state to remote git repo"""
    not_implemented()


@main.command()
def status():
    """Show status"""
    not_implemented()


@main.command()
@click.argument("folder")
def symlink(folder):
    """
    Symlink tracked dotfiles to a given folder

    You'll typically use this for immediate updates, via a synced folder like Dropbox.
    This is optional, and will symlink your dotfiles *in addition* to allowing you to track them via a git repo
    \b
    Example:
        gdot symlink ~/Dropbox/roaming-dotfiles
    """
    not_implemented()


@main.command()
def rm():
    """Untrack a file"""
    not_implemented()


def prettify_epilogs(command=None):
    """
    Conveniently re-arrage docstrings in click-decorated function in such a way that:
    - .help shows the first line of the docstring
    - .epilog shows the rest
    """
    if isinstance(command, click.Command):
        help = command.help
        if help:
            help = help.strip().format(userid=os.environ.get("USER", "USERID"), store_path=GDOT_GIT_STORE)
            command.help = help
            epilog = command.epilog
            if not epilog:
                lines = help.splitlines()
                if len(lines) > 1 and lines[0].strip():
                    command.help = lines.pop(0).strip()
                    epilog = "\n".join(lines)
                    if len(lines) > 1 and not lines[0]:
                        epilog = "\b%s" % epilog

                    epilog = epilog

            if epilog:
                command.epilog = epilog.format(userid=os.environ.get("USER", "USERID"), store_path=GDOT_GIT_STORE)

    if isinstance(command, click.Group) and command.commands:
        for cmd in command.commands.values():
            prettify_epilogs(cmd)


prettify_epilogs(main)
if __name__ == "__main__":
    main()
