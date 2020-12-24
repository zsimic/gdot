from runez.conftest import cli

from gdot import GDEnv
from gdot.commands import main


GDEnv.userid = "tester"
cli.default_main = main
