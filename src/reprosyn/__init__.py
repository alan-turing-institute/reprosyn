# read version from installed package
from importlib.metadata import version
from .run import run

__version__ = version("reprosyn")
