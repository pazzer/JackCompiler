__author__ = 'paulpatterson'

from pathlib import Path
import tempfile
from jack_analyzer.Tokenizer import Tokenizer
from jack_analyzer.VMWriter import VMWriter
from jack_analyzer.CompilationEngine import CompilationEngine


class JackCompiler():

    @classmethod
    def compiler_for_jack_string(cls, jack_string, outfile):

        assert outfile.suffix == ".vm", "{} should have .vm extension".format(outfile.as_posix())

        temporary_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jack")
        temporary_file_path = Path(temporary_file.name)
        with open(temporary_file_path.as_posix(), "w+") as jack_file:
            jack_file.write(jack_string)

        jack_compiler = cls(temporary_file_path)
        jack_compiler.outfile = outfile

        return jack_compiler


    def __init__(self, path=None):
        self.jack_file_paths = []
        self.outfile = None
        self.parse_tree = None
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

    def compile(self):
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
            self.parse_tree = compilation_engine.parse_tree

        if self.outfile is not None:
            self.outfile.unlink()


    # Debugging / testing

    def get_parse_tree(self):
        if self.parse_tree is None:
            self.compile()
        return self.parse_tree

