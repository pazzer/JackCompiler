#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding utf-8 -*-


__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
from pathlib import Path
from JackAnalyzer.Tokenizer import Tokenizer
from JackAnalyzer.CompilationEngine import CompilationEngine
import sys

JACK_ANALYZER_ROOT = Path("/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/JackAnalyzer")


class JackAnalyzer():

    def __init__(self, path=None):
        self.compilation_engine = None
        self.jack_snippet = None
        self.outfile_path = None
        self.jack_file_paths = None
        if path is not None:
            assert path.exists(), "Analysis failed: non-existent path '{}'".format(path.as_posix())
            if path.is_file():
                assert path.suffix == ".jack", \
                    "Analysis failed: user-supplied filename must have '.jack' extension, not '{}'".format(path.suffix)
                self.jack_file_paths = [path]
            else:
                self.jack_file_paths = []
                for child in path.iterdir():
                    if child.is_file() and child.suffix == ".jack":
                        self.jack_file_paths.append(child)

    @classmethod
    def _create_outfile_at_path(cls, path):
        """ Creates a new file at the given path """
        with open(path.as_posix()) as _:
            pass

    @classmethod
    def analyzer_for_snippet(cls, jack_snippet, user_defined_outfile_path=None):
        ja = cls()
        ja.jack_snippet = jack_snippet
        if user_defined_outfile_path is not None:
            # user has requested analysis output be written to a file
            if not user_defined_outfile_path.exists():
                JackAnalyzer._create_outfile_at_path(user_defined_outfile_path)
            ja.outfile_path = user_defined_outfile_path
        return ja

    def _analyze_snippet(self):
        tknzr = Tokenizer(jack_code=self.jack_snippet)
        self.compilation_engine = CompilationEngine(tokenizer=tknzr, output_file_path=self.outfile_path)
        self.compilation_engine.compile()

    def analyze(self, return_results=False):
        if self.jack_snippet is not None:
            self._analyze_snippet()
            if return_results:
                return self.compilation_engine.xml_tree

        else:
            resulting_xml = []
            for path in self.jack_file_paths:
                tknzr = Tokenizer(jack_filepath=path)
                self.outfile_path = path.with_suffix(".xml")
                self.compilation_engine = CompilationEngine(tokenizer=tknzr, output_file_path=self.outfile_path)
                self.compilation_engine.compile()
                if return_results:
                    resulting_xml.append(self.compilation_engine.xml_tree)
            return resulting_xml

if __name__ == "__main__":
    file_or_path = sys.argv[0]
    analyzer = JackAnalyzer(path=file_or_path)
    analyzer.analyze()