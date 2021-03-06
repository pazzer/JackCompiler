__author__ = 'paulpatterson'

from lxml import etree
import unittest
from tests.globals import ACTUAL_COMPARE, EXPECTED_COMPARE, NAND_2_TETRIS

from jack_compiler.JackCompiler import JackCompiler
from jack_compiler.AbstractSyntaxTree import stringify_xml

TESTS_TREE_FILEPATH = NAND_2_TETRIS / "JackCompiler" / "tests" / "SyntaxAnalysisTests.xml"

# todo: Add documentation explaining the mechanics of the testing process in this class
# todo: Add a short docstring to each method

class TestASTGenerationUnofficial(unittest.TestCase):

    def setUp(self):
        self.tests_tree = etree.parse(TESTS_TREE_FILEPATH.as_posix()).getroot()
        self.snippet_wrapper = self.tests_tree.find("snippet_wrapper").text
        self.xml_wrapper = self.tests_tree.find("expected_xml_wrapper/class")

    def _generate_formatted_snippet(self, test_name):
        test_tree = self.tests_tree.find("*[@id='{}']".format(test_name))
        snippet = test_tree.find("jack_snippet").text

        return self.snippet_wrapper.format(snippet)

    def _generate_expected_xml(self, test_name):
        test_tree = self.tests_tree.find("*[@id='{}']".format(test_name))
        expected_xml = test_tree.find("expected_xml")
        expected_xml[0].tail = ""
        return expected_xml[0]

    def _prepare_test(self, test_name):
        formatted_snippet = self._generate_formatted_snippet(test_name)
        expected_xml = self._generate_expected_xml(test_name)

        outfile = NAND_2_TETRIS / ".test_vm.vm"
        compiler = JackCompiler.compiler_for_jack_string(formatted_snippet, outfile)
        compiler.compile()

        actual_string = str(compiler.abstract_syntax_trees[0])
        expected_string = stringify_xml(expected_xml)

        with open(ACTUAL_COMPARE.as_posix(), 'w') as compareOne:
            with open(EXPECTED_COMPARE.as_posix(), 'w') as compareTwo:
                compareOne.write(actual_string)
                compareTwo.write(expected_string)

        return actual_string, expected_string

    def test_trivial_do(self):
        actual, expected = self._prepare_test("trivial_do")
        self.assertMultiLineEqual(actual, expected)

    def test_simple_do(self):
        actual, expected = self._prepare_test("simple_do")
        self.assertMultiLineEqual(actual, expected)

    def test_intermediate_do(self):
        actual, expected = self._prepare_test("intermediate_do")
        self.assertMultiLineEqual(actual, expected)

    def test_advanced_do(self):
        actual, expected = self._prepare_test("advanced_do")
        self.assertMultiLineEqual(actual, expected)

    def test_non_void_return(self):
        actual, expected = self._prepare_test("non_void_return")
        self.assertMultiLineEqual(actual, expected)

    def test_multiple_functions(self):
        actual, expected = self._prepare_test("multiple_functions")
        self.assertMultiLineEqual(actual, expected)

    def test_let(self):
        actual, expected = self._prepare_test("let")
        self.assertMultiLineEqual(actual, expected)

    def test_if(self):
        actual, expected = self._prepare_test("if")
        self.assertMultiLineEqual(actual, expected)

    def test_class_level_variables(self):
        actual, expected = self._prepare_test("class-level variables")
        self.assertMultiLineEqual(actual, expected)

    def test_while(self):
        actual, expected = self._prepare_test("while")
        self.assertMultiLineEqual(actual, expected)

    def test_comment_handling(self):
        actual, expected = self._prepare_test("comment_handling")
        self.assertMultiLineEqual(actual, expected)
