__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
from pathlib import Path
import os
import unittest

from JackAnalyzer.Tokenizer import Tokenizer
from JackAnalyzer.CompilationEngine import stringify_xml

from tests.globals import PROJ_10_DIR

class OfficialTokenizerTests(unittest.TestCase):

    def _prepare_official_tokens_test(self, project, filename):
        jack_file_path = Path(os.path.join(PROJ_10_DIR, project + "/" + filename + ".jack"))
        tknzr = Tokenizer(jack_filepath=jack_file_path)
        actual_xml_tokens = tknzr.tokenize()
        actual_string_tokens = stringify_xml(actual_xml_tokens)

        xml_tokens_file_path = jack_file_path.with_name(filename + "T" + ".xml")
        expected_xml_tokens = ET.parse(xml_tokens_file_path.as_posix())
        expected_string_tokens = stringify_xml(expected_xml_tokens.getroot())

        return actual_string_tokens, expected_string_tokens

    # Square Project

    def test_square__main(self):
        actual, expected = self._prepare_official_tokens_test(project="Square", filename="Main")
        self.assertMultiLineEqual(actual, expected)

    def test_square__square(self):
        actual, expected = self._prepare_official_tokens_test(project="Square", filename="Square")
        self.assertMultiLineEqual(actual, expected)

    def test_square__square_game(self):
        actual, expected = self._prepare_official_tokens_test(project="Square", filename="SquareGame")
        self.assertMultiLineEqual(actual, expected)

    # Array Project

    def test_array__main(self):
        actual, expected = self._prepare_official_tokens_test(project="ArrayTest", filename="Main")
        self.assertMultiLineEqual(actual, expected)

    # ExpressionLessSquare Project

    def test_expressionless_square__main(self):
        actual, expected = self._prepare_official_tokens_test(project="ExpressionLessSquare", filename="Main")
        self.assertMultiLineEqual(actual, expected)

    def test_expressionless_square__square(self):
        actual, expected = self._prepare_official_tokens_test(project="ExpressionLessSquare", filename="Square")
        self.assertMultiLineEqual(actual, expected)

    def test_expressionless_square__square_game(self):
        actual, expected = self._prepare_official_tokens_test(project="ExpressionLessSquare", filename="SquareGame")
        self.assertMultiLineEqual(actual, expected)