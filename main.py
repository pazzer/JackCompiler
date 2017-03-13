__author__ = 'paulpatterson'

from pathlib import Path
from jack_compiler.JackCompiler import JackCompiler
import sys
import os

if __name__ == "__main__":
    path = Path(os.getcwd()) / sys.argv[1]
    compiler = JackCompiler(path=path)
    compiler.compile()
