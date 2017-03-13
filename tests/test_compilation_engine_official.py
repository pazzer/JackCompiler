

import unittest
from pathlib import Path
import xml.etree.ElementTree as ET

from jack_compiler.JackCompiler import JackCompiler
from jack_compiler.CompilationEngine import stringify_xml
from tests.globals import ACTUAL_COMPARE, EXPECTED_COMPARE, PROJ_10_DIR

ARRAY_TEST_DIRECTORY_PATH = \
    Path("/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/nand2tetris/projects/10/ArrayTest")

class TestCompilationEngineOfficial(unittest.TestCase):

    def _prepare_test(self, jack_file_path):
        compiler = JackCompiler(jack_file_path)
        compiler.compile()

        actual_xml = compiler.parse_tree
        actual_string = stringify_xml(actual_xml.getroot())

        expected_xml_file = jack_file_path.with_name("_" + jack_file_path.stem + ".xml")
        expected_xml = ET.parse(expected_xml_file.as_posix())
        expected_string = stringify_xml(expected_xml.getroot())

        with open(ACTUAL_COMPARE.as_posix(), 'w') as compOne:
            with open(EXPECTED_COMPARE.as_posix(), 'w') as compareTwo:
                compOne.write(actual_string)
                compareTwo.write(expected_string)

        return actual_string, expected_string

    # ArrayTest

    def test_array_test__main(self):
        actual, expected = self._prepare_test( Path(PROJ_10_DIR) / "ArrayTest" / "Main.jack" )
        self.assertMultiLineEqual(actual, expected)

    # Square

    def test_square__main(self):
        actual, expected = self._prepare_test( Path(PROJ_10_DIR) / "Square" / "Main.jack" )
        self.assertMultiLineEqual(actual, expected)

    def test_sqaure__square(self):
        actual, expected = self._prepare_test( Path(PROJ_10_DIR) / "Square" / "Square.jack" )
        self.assertMultiLineEqual(actual, expected)

    def test_square__square_game(self):
        actual, expected = self._prepare_test( Path(PROJ_10_DIR) / "Square" / "SquareGame.jack" )
        self.assertMultiLineEqual(actual, expected)

    # ExpressionLessSquare

    def test_expressionless_square__main(self):
        actual, expected = self._prepare_test( Path(PROJ_10_DIR) / "ExpressionLessSquare" / "Main.jack" )
        self.assertMultiLineEqual(actual, expected)

    def test_expressionless_square__square(self):
        actual, expected = self._prepare_test( Path(PROJ_10_DIR) / "ExpressionLessSquare" / "Square.jack" )
        self.assertMultiLineEqual(actual, expected)

    def test_expressionless_square__square_game(self):
        actual, expected = self._prepare_test( Path(PROJ_10_DIR) / "ExpressionLessSquare" / "SquareGame.jack" )
        self.assertMultiLineEqual(actual, expected)


