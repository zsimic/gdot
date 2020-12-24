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

from gdot import complain, GDotX


GDOTX = None  # type: GDotX


def not_implemented():
    caller = runez.system.find_caller_frame()
    cmd = "gdot %s" % caller.f_code.co_name
    sys.exit("%s is not yet implemented" % runez.red(cmd))


def require_userid():
    if not GDOTX.gv.userid:
        GDOTX.abort("Could not determine userid")


@runez.click.group(epilog=__doc__)
@runez.click.version(message="gdot %(version)s")
@runez.click.debug()
@runez.click.dryrun()
@runez.click.color()
def main(debug):
    """Git my dotfiles!"""
    global GDOTX
    if os.geteuid() == 0:
        complain("%s was not designed to run as %s\n\n" % (runez.blue("gdot"), runez.red("root")))
        complain("Please %s if you see a use-case for that on %s\n\n" % (runez.yellow("let us know"), GDotX.gv.issues_url))
        sys.exit(1)

    GDOTX = GDotX()
    runez.log.setup(debug=debug, console_format="%(levelname)s %(message)s", locations=None, greetings=":: {argv}")


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
    require_userid()
    GDOTX.attach(url)


@main.command()
def detach():
    """
    Detach from remote
    All local files will remain as-is,
    but gdot won't consider them linked with any remote
    """
    not_implemented()


@main.command()
def diagnostics():
    """Show system information"""
    print(GDOTX.get_diagnostics())


@main.command()
def diff():
    """Show what's changed since last pull/push/sync"""
    not_implemented()


@main.command()
def git():
    """
    Run a git command on the dotfiles repo

    This is the same as running:
        cd {default_store}
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


runez.click.prettify_epilogs(main, formatter=GDotX.gv.formatted)
if __name__ == "__main__":  # pragma: no cover, invoked this way by debugger
    main()
