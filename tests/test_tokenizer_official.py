__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
import unittest

from jack_analyzer.Tokenizer import Tokenizer
from jack_analyzer.CompilationEngine import stringify_xml

from tests.globals import PROJ_10_DIR
from tests.globals import NAND_2_TETRIS, ACTUAL_COMPARE, EXPECTED_COMPARE

class OfficialTokenizerTests(unittest.TestCase):

    def _write_results_to_compare_files(self, actual_vm, expected_vm):
        with open(ACTUAL_COMPARE.as_posix(), 'w') as compareOne:
            with open(EXPECTED_COMPARE.as_posix(), 'w') as compareTwo:
                compareOne.write(actual_vm)
                compareTwo.write(expected_vm)

    def _prepare_official_tokens_test(self, project, filename):
        jack_file_path = PROJ_10_DIR / project / (filename + ".jack")
        tknzr = Tokenizer(jack_filepath=jack_file_path)
        actual_xml_tokens = tknzr.tokenize()
        actual_string_tokens = stringify_xml(actual_xml_tokens)

        xml_tokens_file_path = jack_file_path.with_name(filename + "T" + ".xml")
        expected_xml_tokens = ET.parse(xml_tokens_file_path.as_posix())
        expected_string_tokens = stringify_xml(expected_xml_tokens.getroot())

        return actual_string_tokens, expected_string_tokens

    # Square Project

    # def test_square__main(self):
    #     actual, expected = self._prepare_official_tokens_test(project="Square", filename="Main")
    #     self._write_results_to_compare_files(actual, expected)
    #     self.assertMultiLineEqual(actual, expected)

    def test_square__square(self):
        actual, expected = self._prepare_official_tokens_test(project="Square", filename="Square")
        self._write_results_to_compare_files(actual, expected)
        self.assertMultiLineEqual(actual, expected)

    # def test_square__square_game(self):
    #     actual, expected = self._prepare_official_tokens_test(project="Square", filename="SquareGame")
    #     self.assertMultiLineEqual(actual, expected)
    #
    # # Array Project
    #
    # def test_array__main(self):
    #     actual, expected = self._prepare_official_tokens_test(project="ArrayTest", filename="Main")
    #     self.assertMultiLineEqual(actual, expected)
    #
    # # ExpressionLessSquare Project
    #
    # def test_expressionless_square__main(self):
    #     actual, expected = self._prepare_official_tokens_test(project="ExpressionLessSquare", filename="Main")
    #     self.assertMultiLineEqual(actual, expected)
    #
    # def test_expressionless_square__square(self):
    #     actual, expected = self._prepare_official_tokens_test(project="ExpressionLessSquare", filename="Square")
    #     self.assertMultiLineEqual(actual, expected)
    #
    # def test_expressionless_square__square_game(self):
    #     actual, expected = self._prepare_official_tokens_test(project="ExpressionLessSquare", filename="SquareGame")
    #     self.assertMultiLineEqual(actual, expected)
