__author__ = 'paulpatterson'

from pathlib import Path
import tempfile
from jack_compiler.Tokenizer import Tokenizer
from jack_compiler.VMWriter import VMWriter
from jack_compiler.CompilationEngine import CompilationEngine


class JackCompiler():

    def __init__(self, path=None):
        """ Creates a new JackCompiler instance. If path is set is should point to a jack file, or a directory
        containing at least one such file. """
        self.jack_file_paths = []
        self._abstract_syntax_trees = []
        self.outfile = None
        self.using_temporary_file_path = False

        assert path.exists(), \
            "Compilation failed: non-existent path '{}'".format(path.as_posix())
        if path.is_file():
            assert path.suffix == ".jack", \
                "Compilation failed: supplied filename must have '.jack' extension, not '{}'".format(path.suffix)
            self.jack_file_paths = [path]
        else:
            for child in path.iterdir():
                if child.is_file() and child.suffix == ".jack":
                    self.jack_file_paths.append(child)

    @classmethod
    def compiler_for_jack_string(cls, jack_string, outfile):
        """ Allows clients to compile a string of valid jack code. The resulting vm is written to outfile. """
        assert outfile.suffix == ".vm", "{} should have .vm extension".format(outfile.as_posix())

        temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jack")
        temporary_file_path = Path(temporary_file.name)
        with open(temporary_file_path.as_posix(), "w+") as jack_file:
            jack_file.write(jack_string)

        jack_compiler = cls(temporary_file_path)
        jack_compiler.outfile = outfile

        return jack_compiler

    def compile(self):
        """ Compiles every .jack file contained within jack_file_paths """
        for jack_file in self.jack_file_paths:
            if self.outfile is not None:
                vm_file_path = self.outfile
            else:
                jack_file_name = jack_file.stem
                vm_file_path = jack_file.with_name(jack_file_name + ".vm")

            tokenizer = Tokenizer(jack_filepath=jack_file)
            vm_writer = VMWriter(vm_file_path)

            compilation_engine = CompilationEngine(tokenizer, vm_writer)
            compilation_engine.compile()
            self.abstract_syntax_trees.append(compilation_engine.ast)

        if self.outfile is not None:
            self.outfile.unlink()

    # Debugging / testing

    @property
    def abstract_syntax_trees(self):
        """ List containing an AbstractSyntaxTree instance for every .jack file that was successfully compiled. """
        return self._abstract_syntax_trees


