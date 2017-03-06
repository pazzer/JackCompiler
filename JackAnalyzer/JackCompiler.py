__author__ = 'paulpatterson'

import sys
from pathlib import Path
import os
from JackAnalyzer.Tokenizer import Tokenizer
from JackAnalyzer.CompilationEngine import CompilationEngine
## Input
## $ JackCompiler.py [file.jack|directoryName]
##
## Output
## If the input was a .jack file, the output is a single .vm file with the same stem as the jack file.
## If the input was a directory, create one .vm file for every .jack file in the directory, and place all of the
## generated .vm files in the same directory as the jack files.
##
## Implementation Notes
##
## For each source .jack file, the compiler creates a JackTokenizer and an output .vm file. The compiler then uses
## the SymbolTable, CompilationEngine, and VMWriter modules to write the VM code into the output .vm file.


class JackCompiler():

    def __init__(self, path):
        self.jack_file_paths = []
        assert path.exists(), \
            "Compilation failed: non-existent path '{}'".format(path.as_posix())
        if path.is_file():
            assert path.suffix == ".jack", \
                "Compilation failed: user-supplied filename must have '.jack' extension, not '{}'".format(path.suffix)
            self.jack_file_paths = [path]
        else:
            for child in path.iterdir():
                if child.is_file() and child.suffix == ".jack":
                    self.jack_file_paths.append(child)

    def compile(self):
        for jack_file in self.jack_file_paths:
            ## Compiling a new .jack file (jack class)
            jack_file_name = jack_file.stem
            tokenizer = Tokenizer(jack_filepath=jack_file)
            vm_file = jack_file.with_name(jack_file_name + ".vm")
            with open(vm_file, mode="w+") as outfile:

                engine = CompilationEngine(tokenizer, outfile)





if __name__ == "__main__":
    user_supplied_file_or_folder = sys.argv[1]
    path = Path(os.getcwd()) / user_supplied_file_or_folder
    compiler = JackCompiler(path=user_supplied_file_or_folder)
    compiler.compile()

