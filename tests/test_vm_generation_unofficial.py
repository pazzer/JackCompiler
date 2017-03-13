__author__ = 'paulpatterson'

from unittest import TestCase
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
from collections import namedtuple
import tempfile

from jack_analyzer.CompilationEngine import stringify_xml
from jack_analyzer.JackCompiler import JackCompiler
from tests.globals import NAND_2_TETRIS, ACTUAL_COMPARE, EXPECTED_COMPARE


TestStrings = namedtuple("TestStrings", "actual expected")

TESTFILE = NAND_2_TETRIS / "JackAnalyzer" / "tests" / "CompilationTests.xml"
PARSE_TREE = NAND_2_TETRIS / "JackAnalyzer" / "tests" / "ParseTree.xml"


class CompilerVMGeneration(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tests = ET.parse(TESTFILE.as_posix()).getroot()

        cls.jack_project_directory = None
        cls.jack_file_path = None
        cls.vm_file_path = None

    def tearDown(self):
        if self.jack_project_directory is not None:
            parent_directory = self.jack_project_directory.parent
            shutil.rmtree(parent_directory.as_posix())
            self.jack_project_directory = None


    def _get_test_components(self, test_id):
        test_tree = self.tests.find("*[@id='{}']".format(test_id))
        expected_vm = test_tree.find("expected_vm").text.strip()
        jack_code = test_tree.find("jack_class").text
        return jack_code, expected_vm

    def make_temporary_test_directory(self, dir_name):
        tmp_dir = Path(tempfile.mkdtemp())
        proj_dir = tmp_dir / dir_name
        proj_dir.mkdir(parents=False)
        return proj_dir

    def set_up_compilable_jack_project(self, test_id, jack_code):
        self.jack_project_directory= self.make_temporary_test_directory(test_id)
        self.jack_file_path = self.jack_project_directory / "Main.jack"
        self.vm_file_path = self.jack_file_path.with_name("Main.vm")
        with open(self.jack_file_path.as_posix(), "w+") as jack_file:
            jack_file.write(jack_code)

    def _write_results_to_compare_files(self, actual_vm, expected_vm):
        with open(ACTUAL_COMPARE.as_posix(), 'w') as compareOne:
            with open(EXPECTED_COMPARE.as_posix(), 'w') as compareTwo:
                compareOne.write(actual_vm)
                compareTwo.write(expected_vm)

    def _write_parse_tree(self, xml):
        parse_tree = stringify_xml(xml.getroot())
        with open(PARSE_TREE.as_posix(), "w") as astfile:
            astfile.write(parse_tree)

    def _vm_strings_for_test(self, test_id):
        jack_code, expected_vm = self._get_test_components(test_id)

        # the next step sets the value of self.jack_project_directory, self.jack_file_path, and self.vm_file_path
        self.set_up_compilable_jack_project(test_id, jack_code)

        try:
            compiler = JackCompiler(path=self.jack_file_path)
            compiler.compile()
        except Exception as e:
            print(e)
            return None

        self._write_parse_tree(compiler.parse_tree)
        with open(self.vm_file_path.as_posix()) as vmfile:
            actual_vm = vmfile.read().strip()
            test_strings = TestStrings(actual_vm, expected_vm)

        self._write_results_to_compare_files(test_strings.actual, test_strings.expected)

        return test_strings

    def test_numbers(self):
        test_strings = self._vm_strings_for_test("Numbers")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_seven(self):
        test_strings = self._vm_strings_for_test("Seven")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_square_main(self):
        test_strings = self._vm_strings_for_test("Square-Main")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_c2b_main(self):
        test_strings = self._vm_strings_for_test("C2BMain")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_if(self):
        test_strings = self._vm_strings_for_test("simple-if")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_if_else(self):
        test_strings = self._vm_strings_for_test("simple-if-else")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_nested_if_else(self):
        test_strings = self._vm_strings_for_test("simple-if-else")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_while(self):
        test_strings = self._vm_strings_for_test("simple-while")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_convert_to_binary(self):
        test_strings = self._vm_strings_for_test("ConvertToBin")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_simple_array(self):
        test_strings = self._vm_strings_for_test("simple-array")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_two_arrays(self):
        test_strings = self._vm_strings_for_test("two-simple-arrays")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_index_assignment(self):
        test_strings = self._vm_strings_for_test("indexed-assignment")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_complex_arrays_fragment(self):
        test_strings = self._vm_strings_for_test("complex-arrays-fragment")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_average(self):
        test_strings = self._vm_strings_for_test("Average")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_pong_main(self):
        test_strings = self._vm_strings_for_test("Pong-Main")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_pong_ponggame(self):
        test_strings = self._vm_strings_for_test("Pong-PongGame")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_pong_bat(self):
        test_strings = self._vm_strings_for_test("Pong-Bat")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_pong_ball(self):
        test_strings = self._vm_strings_for_test("Pong-Ball")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_square_squaregame(self):
        test_strings = self._vm_strings_for_test("Square-SquareGame")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_square_square(self):
        test_strings = self._vm_strings_for_test("Square-Square")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)

    def test_complex_arrays(self):
        test_strings = self._vm_strings_for_test("ComplexArrays")
        self.assertIsNotNone(test_strings, "failed to generate either expected vm code, actual vm code, or both.")
        self.assertMultiLineEqual(test_strings.actual, test_strings.expected)
