import os
import sys

import runez


def require_files(*paths):
    for path in paths:
        if not os.path.isfile(path):
            return "File '%s' does not exist" % runez.short(path)


def require_folders(*paths):
    for path in paths:
        if not os.path.isdir(path):
            return "Folder '%s' does not exist" % runez.short(path)


class DCService(object):
    def __init__(self, name):
        self.name = name
        self.repo = os.getcwd()
        self.origin = os.path.join(self.repo, name)
        self.docker_compose = os.path.join(self.origin, "docker-compose.yml")
        self.origin_root = os.path.join(self.origin, "root")
        self.target = os.path.join("/srv", name)
        self.target_root = os.path.join(self.target, "root")

    def problem(self, require_installed):
        p = require_folders(self.origin, self.origin_root)
        if not p:
            p = require_files(self.docker_compose)

        if not p and require_installed:
            p = require_folders(self.target, self.target_root)

        return p

    def validate(self, require_installed=True):
        problem = self.problem(require_installed)
        if problem:
            sys.stderr.write("%s\n" % runez.red(problem))
            sys.exit(1)

    def install(self):
        self.validate(require_installed=False)
        if os.path.isdir(self.target):
            print("%s is already installed" % self.name)
            return

        runez.run("sudo", "mkdir", self.target)
        runez.run("sudo", "chown", os.environ.get("USER"), self.target)
        runez.run("sudo", "rsync", "-aHJ", "%s/" % self.origin, self.target)

    def start(self):
        self.validate()
        with runez.CurrentFolder(self.target):
            runez.run("docker-compose", "up", "-d")

    def stop(self):
        self.validate()
        with runez.CurrentFolder(self.target):
            runez.run("docker-compose", "stop")

    def sync(self):
        self.validate()
        runez.run("sudo", "rsync", "-aHJ", "%s/" % self.target, self.origin)

    def upgrade(self):
        self.stop()
        with runez.CurrentFolder(self.target):
            runez.run("docker-compose", "pull")
            runez.run("docker-compose", "prune", "-f")

        self.start()
