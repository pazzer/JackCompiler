__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
import unittest
from pathlib import Path
from tests.globals import ACTUAL_COMPARE, EXPECTED_COMPARE

from JackAnalyzer.JackAnalyzer import JackAnalyzer
from JackAnalyzer.CompilationEngine import stringify_xml

TESTS_TREE_FILEPATH = Path("/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/JackAnalyzer/tests/Tests.xml")


class CustomAnalyzerTests(unittest.TestCase):

    def setUp(self):
        self.tests_tree = ET.parse(TESTS_TREE_FILEPATH.as_posix()).getroot()
        self.snippet_wrapper = self.tests_tree.find("snippet_wrapper").text
        self.xml_wrapper = self.tests_tree.find("expected_xml_wrapper/class")

    def _generate_formatted_snippet(self, test_name):
        test_tree = self.tests_tree.find("*[@id='{}']".format(test_name))
        snippet = test_tree.find("jack_snippet").text

        return self.snippet_wrapper.format(snippet)

    def _generate_expected_xml(self, test_name):
        test_tree = self.tests_tree.find("*[@id='{}']".format(test_name))
        expected_xml = test_tree.find("expected_xml")
        offset = 0
        for each in list(expected_xml):
            self.xml_wrapper.insert(3 + offset, each)
            offset += 1
        return self.xml_wrapper

    def _prepare_test(self, test_name):
        formatted_snippet = self._generate_formatted_snippet(test_name)
        expected_xml = self._generate_expected_xml(test_name)

        analyzer = JackAnalyzer.analyzer_for_snippet(formatted_snippet)
        actual_xml = analyzer.analyze(return_results=True)

        actual_string = stringify_xml(actual_xml.getroot())
        expected_string = stringify_xml(expected_xml)

        with open(ACTUAL_COMPARE.as_posix(), 'w') as compOne:
            with open(EXPECTED_COMPARE.as_posix(), 'w') as compareTwo:
                compOne.write(actual_string)
                compareTwo.write(expected_string)

        actual_string = stringify_xml(actual_xml.getroot())
        expected_string = stringify_xml(expected_xml)

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
