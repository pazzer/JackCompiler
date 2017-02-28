#!/Library/Frameworks/Python.framework/Versions/3.4/bin/python3.4
# -*- coding utf-8 -*-


__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import sys
import os
from JackAnalyzer.Tokenizer import Tokenizer
from JackAnalyzer.CompilationEngine import CompilationEngine

JACK_ANALYZER_ROOT = "/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/JackAnalyzer"

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
    def create_outfile_at_path(cls, path):
        with open(path.as_posix()) as _:
            pass

    @classmethod
    def analyzer_for_snippet(cls, jack_snippet, user_defined_outfile_path=None):
        analyzer = cls()
        analyzer.jack_snippet = jack_snippet
        if user_defined_outfile_path is None:
            user_defined_outfile_path = Path(os.path.join(JACK_ANALYZER_ROOT, "jack_analyzed.xml"))
            if not user_defined_outfile_path.exists():
                JackAnalyzer.create_outfile_at_path(user_defined_outfile_path)
            analyzer.outfile_path = user_defined_outfile_path
        else:
            analyzer.outfile_path = user_defined_outfile_path
        return analyzer


    def _analyze_snippet(self):
        tknzr = Tokenizer(jack_code=self.jack_snippet)
        self.compilation_engine = CompilationEngine(tokenizer=tknzr, output_file_path=self.outfile_path)
        self.compilation_engine.compile()


    def _contents_of_outfile(self):
        return ET.parse(self.outfile_path.as_posix())

    def analyze(self, return_results=False):
        if self.jack_snippet is not None:
            self._analyze_snippet()
            if return_results:
                return self._contents_of_outfile()

        else:
            resulting_xml = []
            for path in self.jack_file_paths:
                tknzr = Tokenizer(jack_filepath=path)
                self.outfile_path = path.with_suffix(".xml")
                self.compilation_engine = CompilationEngine(tokenizer=tknzr, output_file_path=self.outfile_path)
                self.compilation_engine.compile()
                if return_results:
                    resulting_xml.append(self._contents_of_outfile())
            return resulting_xml