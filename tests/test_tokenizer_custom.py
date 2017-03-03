
import unittest

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
        expected = [("keyword", " constructor "), ("identifier", " Fraction "), ("identifier", " new "),
                    ("symbol", " ( "), ("keyword", " int "), ("identifier", " x "), ("symbol", " , "),
                    ("keyword", " int "), ("identifier", " y "), ("symbol", " ) "), ("symbol", " { ")]
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
                    ("keyword", " int "), ("identifier", " numerator "), ("symbol", " , "),
                    ("identifier", " denominator "), ("symbol", " ; "), ("symbol", " } ")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    # Testing 'advance()'
    def test_advance_a(self):
        jack_snippet = "constructor Fraction new(int x, int y) {"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        tokenizer.advance()
        tokenizer.advance()
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue( \
            xml.text == " new ", "advance() returned unexpected result: got '', expected 'new'".format(xml.text))

    def test_advance_b(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        for _ in range(10):
            tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue( \
            xml.text == " other ", "advance() returned unexpected result: got '', expected 'other'".format(xml.text))

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
        self.assertTrue( \
            xml.text == " ; ", "advance() returned unexpected result: got '', expected ';'".format(xml.text))
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(\
            xml.text == " ; ", "advance() returned unexpected result: got '', expected ';'".format(xml.text))

    def test_handling_comments(self):
        jack_snippet = """
        class Main { // Ignore this...
            field int numerator, denominator; // ... and this!
        }
        """
        expected = [("keyword", " class "), ("identifier", " Main "), ("symbol", " { "), ("keyword", " field "),
                    ("keyword", " int "), ("identifier", " numerator "), ("symbol", " , "),
                    ("identifier", " denominator "), ("symbol", " ; "), ("symbol", " } ")]

        tokenizer = Tokenizer(jack_code=jack_snippet)
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
