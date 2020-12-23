Git my dotfiles!
================

.. image:: https://img.shields.io/pypi/v/pickley.svg
    :target: https://pypi.org/project/gdot/
    :alt: Version on pypi

.. image:: https://github.com/codrsquad/gdot/workflows/Tests/badge.svg
    :target: https://github.com/codrsquad/gdot/actions
    :alt: Tested with Github Actions

.. image:: https://img.shields.io/pypi/pyversions/pickley.svg
    :target: https://github.com/codrsquad/gdot
    :alt: Python versions tested (link to github project)


``gdot`` is a python CLI that allows to easily roam one's dotfile configs
(such as ``~/.bashrc`` and ``~/.config/...``) between multiple machines.


Getting started::

    # On first login, associate your local files to a remote git repo
    gdot attach github:myuserid

    # Pull changes from your remote git store any time
    gdot pull

    # Add some files to track
    gdot add ~/.bashrc ~/.config/htop/

    # When you made some local changes, push them to your git store
    gdot push

    # Optionally, you can specify a commit message
    gdot push -m "Changed qtile settings"

    # See what's changed since you last push/pull-ed
    gdot status
    gdot diff


Installation
============

Install it with pickley_::

    pickley install gdot            # Grab the latest
    pickley install gdot==1.0.0     # Or pin to a specific version


Or in a venv::

    python3 -mvenv ~/.local/venvs/gdot
    ~/.local/venvs/gdot/bin/pip install gdot

    # Then put a symlink to a folder that is in your PATH:
    ln -s ~/.local/venvs/gdot/bin/gdot ~/.local/bin/gdot

    # Or simply alias it:
    alias gdot=~/.local/venvs/gdot/bin/gdot

    # You can upgrade it like so:
    ~/.local/venvs/gdot/bin/pip install -U gdot

    # Or pin to a specific version:
    ~/.local/venvs/gdot/bin/pip install -U gdot==1.0.0


.. _pickley: https://pypi.org/project/pickley/
