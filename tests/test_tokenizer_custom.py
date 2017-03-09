
import unittest
import tempfile
import os
from pathlib import  Path

from jack_analyzer.Tokenizer import Tokenizer


class CustomTokenizerTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
         posix_string = tempfile.NamedTemporaryFile(delete=False).name
         cls.temporary_file_path = Path(posix_string)

    @classmethod
    def tearDownClass(cls):
        os.unlink(cls.temporary_file_path.as_posix())

    def write_snippet_to_temporary_file(self, jack_snippet):
        with open(self.temporary_file_path.as_posix(), "w") as tmpfile:
            tmpfile.write(jack_snippet)

    def tokenize_snippet(self, jack_snippet):
        self.write_snippet_to_temporary_file(jack_snippet)
        tknzr = Tokenizer(jack_filepath=self.temporary_file_path)
        xml = tknzr.tokenize()
        return [(child.tag, child.text) for child in xml]

    def test_call(self):
        snippet = "point.getx()"
        actual = self.tokenize_snippet(snippet)
        expected = [("identifier", " point "), ("symbol", " . "), ("identifier", " getx "), ("symbol", " ( "),
                    ("symbol", " ) ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))

    def test_constant_let(self,):
        snippet = "let x = 10"
        actual = self.tokenize_snippet(snippet)
        expected = [("keyword", " let "), ("identifier", " x "), ("symbol", " = "), ("integerConstant", " 10 ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))

    def test_symbolic_let(self):
        snippet = "var int g;"
        actual = self.tokenize_snippet(snippet)
        expected = [("keyword", " var "), ("keyword", " int "), ("identifier", " g "), ("symbol", " ; ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))

    def test_return(self):
        snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        actual = self.tokenize_snippet(snippet)
        expected = [("keyword", " return "), ("identifier", " Fraction "), ("symbol", " . "), ("identifier", " new "),
                    ("symbol", " ( "), ("identifier", " sum "), ("symbol", " , "), ("identifier", " denominator "),
                    ("symbol", " * "), ("identifier", " other "), ("symbol", " . "), ("identifier", " getDenominator "),
                    ("symbol", " ( "), ("symbol", " ) "), ("symbol", " ) "), ("symbol", " ; ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))

    def test_do(self):
        snippet = 'do Output.printString("/");'
        actual = self.tokenize_snippet(snippet)
        expected = [("keyword", " do "), ("identifier", " Output "), ("symbol", " . "), ("identifier", " printString "),
                    ("symbol", " ( "), ("stringConstant", ' / '), ("symbol", " ) "), ("symbol", " ; ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))


    def test_constructor(self):
        snippet = "constructor Fraction new(int x, int y) {"
        actual = self.tokenize_snippet(snippet)
        expected = [("keyword", " constructor "), ("identifier", " Fraction "), ("identifier", " new "),
                    ("symbol", " ( "), ("keyword", " int "), ("identifier", " x "), ("symbol", " , "),
                    ("keyword", " int "), ("identifier", " y "), ("symbol", " ) "), ("symbol", " { ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))

    def test_special_symbols(self):
        snippet = "x > y; y < z"
        actual = self.tokenize_snippet(snippet)
        expected = [("identifier", " x "), ("symbol", " > "), ("identifier", " y "), ("symbol", " ; "),
                    ("identifier", " y "), ("symbol", " < "), ("identifier", " z ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))

    def test_class_constructor(self):
        snippet = """
        class Main {
            field int numerator, denominator;
        }
        """
        actual = self.tokenize_snippet(snippet)
        expected = [("keyword", " class "), ("identifier", " Main "), ("symbol", " { "), ("keyword", " field "),
                    ("keyword", " int "), ("identifier", " numerator "), ("symbol", " , "),
                    ("identifier", " denominator "), ("symbol", " ; "), ("symbol", " } ")]
        self.assertListEqual(actual, expected, "failed {}".format(snippet))

    # Testing 'advance()'
    def test_advance_a(self):
        jack_snippet = "constructor Fraction new(int x, int y) {"
        self.write_snippet_to_temporary_file(jack_snippet)

        tokenizer = Tokenizer(self.temporary_file_path)
        tokenizer.advance()
        tokenizer.advance()
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue( \
            xml.text == " new ", "advance() returned unexpected result: got '', expected 'new'".format(xml.text))

    def test_advance_b(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        self.write_snippet_to_temporary_file(jack_snippet)

        tokenizer = Tokenizer(self.temporary_file_path)
        for _ in range(10):
            tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue( \
            xml.text == " other ", "advance() returned unexpected result: got '', expected 'other'".format(xml.text))

    def test_advance_at_init(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        self.write_snippet_to_temporary_file(jack_snippet)

        tokenizer = Tokenizer(self.temporary_file_path)
        self.assertIsNone(tokenizer.current_token)

    def test_advance_at_end(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        self.write_snippet_to_temporary_file(jack_snippet)

        tokenizer = Tokenizer(self.temporary_file_path)
        for _ in range(100):
            tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue( \
            xml.text == " ; ", "advance() returned unexpected result: got '', expected ';'".format(xml.text))
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(\
            xml.text == " ; ", "advance() returned unexpected result: got '', expected ';'".format(xml.text))

    def test_handling_comments(self):
        snippet = """
        class Main { // Ignore this...
            field int numerator, denominator; // ... and this!
        }
        """
        expected = [("keyword", " class "), ("identifier", " Main "), ("symbol", " { "), ("keyword", " field "),
                    ("keyword", " int "), ("identifier", " numerator "), ("symbol", " , "),
                    ("identifier", " denominator "), ("symbol", " ; "), ("symbol", " } ")]

        self.write_snippet_to_temporary_file(snippet)

        tokenizer = Tokenizer(self.temporary_file_path)
        tokenizer.advance()  # ...arrives at 'class'
        tokenizer.advance()  # ...eats 'class', now at 'Main'
        tokenizer.advance()  # ...eats 'Main', now at '{'
        tokenizer.advance()  # ...eats 'Main', IGNORES COMMENT, now at 'field'
        self.assertTrue(tokenizer.current_token.text == " field ")
        tokenizer.advance()  # ...eats 'field', now at 'int'
        tokenizer.advance()  # ...eats 'int', now at 'numerator'
        tokenizer.advance()  # ...eats 'numerator', now at ','
        tokenizer.advance()  # ...eats ',' now at 'denominator'
        tokenizer.advance()  # ...eats 'denominator' now at ';'
        tokenizer.advance()  # ...eats ';', IGNORES COMMENT, now at '}'
        self.assertTrue(tokenizer.current_token.text == " } ")
