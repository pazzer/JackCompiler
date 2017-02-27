
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
import os

from JackAnalyzer.Tokenizer import Tokenizer


class CustomTokenizerTests(unittest.TestCase):

    def tokenize(self, jack_snippet):
        tknzr = Tokenizer(jack_code=jack_snippet)
        xml = tknzr.tokenize()
        return [(child.tag, child.text) for child in xml]

    def test_call(self):
        jack_snippet = "point.getx()"
        actual = self.tokenize(jack_snippet)
        expected = [("identifier", " point "), ("symbol", " . "), ("identifier", " getx "), ("symbol", " ( "),
                    ("symbol", " ) ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_constant_let(self,):
        jack_snippet = "let x = 10"
        actual = self.tokenize(jack_snippet)
        expected = [("keyword", " let "), ("identifier", " x "), ("symbol", " = "), ("integerConstant", " 10 ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_symbolic_let(self):
        jack_snippet = "var int g;"
        actual = self.tokenize(jack_snippet)
        expected = [("keyword", " var "), ("keyword", " int "), ("identifier", " g "), ("symbol", " ; ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_return(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        actual = self.tokenize(jack_snippet)
        expected = [("keyword", " return "), ("identifier", " Fraction "), ("symbol", " . "), ("identifier", " new "),
                    ("symbol", " ( "), ("identifier", " sum "), ("symbol", " , "), ("identifier", " denominator "),
                    ("symbol", " * "), ("identifier", " other "), ("symbol", " . "), ("identifier", " getDenominator "),
                    ("symbol", " ( "), ("symbol", " ) "), ("symbol", " ) "), ("symbol", " ; ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_do(self):
        jack_snippet = 'do Output.printString("/");'
        actual = self.tokenize(jack_snippet)
        expected = [("keyword", " do "), ("identifier", " Output "), ("symbol", " . "), ("identifier", " printString "),
                    ("symbol", " ( "), ("stringConstant", ' / '), ("symbol", " ) "), ("symbol", " ; ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))


    def test_constructor(self):
        jack_snippet = "constructor Fraction new(int x, int y) {"
        actual = self.tokenize(jack_snippet)
        expected = [("keyword", " constructor "), ("identifier", " Fraction "), ("identifier", " new "), ("symbol", " ( "),
            ("keyword", " int "), ("identifier", " x "), ("symbol", " , "), ("keyword", " int "), ("identifier", " y "),
            ("symbol", " ) "), ("symbol", " { ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_special_symbols(self):
        jack_snippet = "x > y; y < z"
        actual = self.tokenize(jack_snippet)
        expected = [("identifier", " x "), ("symbol", " > "), ("identifier", " y "), ("symbol", " ; "),
                    ("identifier", " y "), ("symbol", " < "), ("identifier", " z ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_class_constructor(self):
        jack_snippet = """
        class Main {
            field int numerator, denominator;
        }
        """
        actual = self.tokenize(jack_snippet)
        expected = [("keyword", " class "), ("identifier", " Main "), ("symbol", " { "), ("keyword", " field "),
                    ("keyword", " int "), ("identifier", " numerator "), ("symbol", " , "), ("identifier", " denominator "),
                    ("symbol", " ; "), ("symbol", " } ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    # Testing 'advance()'
    def test_advance_a(self):
        jack_snippet = "constructor Fraction new(int x, int y) {"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        tokenizer.advance()
        tokenizer.advance()
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(xml.text == " new ", "advance() returned unexpected result: got '', expected 'new'".format(xml.text))

    def test_advance_b(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        for _ in range(10):
            tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(xml.text == " other ", "advance() returned unexpected result: got '', expected 'other'".format(xml.text))

    def test_advance_at_init(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        self.assertIsNone(tokenizer.current_token)

    def test_advance_at_end(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        for _ in range(100):
            tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(xml.text == " ; ", "advance() returned unexpected result: got '', expected ';'".format(xml.text))
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(xml.text == " ; ", "advance() returned unexpected result: got '', expected ';'".format(xml.text))

    # Testing 'has_more_tokens()'
    def test_has_more_tokens(self):
        jack_snippet = "return 12"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        self.assertTrue(tokenizer.has_more_tokens(), "'has_more_tokens()' reporting False - expected True")
        tokenizer.advance()
        tokenizer.advance()
        self.assertFalse(tokenizer.has_more_tokens(), "'has_more_tokens()' reporting True - expected False")


    def test_keyword(self):
        jack_snippet = "return 12"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        tokenizer.advance()
        with self.assertRaises(AssertionError):
            tokenizer.identifier()
        self.assertTrue(tokenizer.keyword() == " return ", "Expected current_token to be of type 'keyword'")

    def test_int_val(self):
        jack_snippet = "return 12"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        tokenizer.advance()
        tokenizer.advance()
        with self.assertRaises(AssertionError):
            tokenizer.keyword()
        self.assertTrue(tokenizer.int_val() == 12, "Expected current_token to be of type 'int_const'")

