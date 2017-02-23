__author__ = 'paulpatterson'

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.dom import minidom
from pathlib import Path
from collections import namedtuple
import re
import unittest

KEYWORDS = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean",
            "void", "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"]
RE_KEYWORD = re.compile("(?:\s*)(?P<KEYWORD>{})".format("|".join(KEYWORDS)))

RE_SYMBOL = re.compile("(?:\s*)(?P<SYMBOL>\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|\-|\*|\/|\&|\||\<|\>|\=|\~)")

RE_INT_CONST = re.compile("(?:\s*)(?P<INT_CONST>[0-9]+)")

RE_IDENTIFIER = re.compile("(?:\s*)(?P<IDENTIFIER>[a-zA-Z_][a-zA-Z0-9_]*)")

RE_STRING_CONST = re.compile("(?:\s*)(?P<STRING_CONST>\"[^\"\n]+\")")

Span = namedtuple("Span", "start end")
JackMatch = namedtuple("JackMatch", "tag text span")

class Tokenizer():

    def __init__(self, jack_code=None, jack_filepath=None):
        """ Opens the input file/stream and gets ready to tokenize it. """
        if jack_filepath is not None:
            with open(jack_filepath.as_posix(), 'r') as jack_file:
                self.input = jack_file.read()
        else:
            self._input = jack_code
        self.tokens = Element("tokens")
        self._pos = 0


    def tokenize(self):
        """ Tokenizes the entire input string in one go (useful for testing) """
        next_token = self.advance()
        while next_token is not None:
            next_token = self.advance()

        return self.tokens

    def _lookahead(self):
        def unpack_match(token_match):
            span = Span(token_match.span()[0], token_match.span()[1])
            group_names = list(token_match.groupdict().keys())
            assert len(group_names) == 1, "Expected one named group, but got {} ({})".format(len(group_names), group_names)
            tag = group_names[0]
            text = token_match.groups(tag)[0]
            return JackMatch(tag, text, span)

        match_args = self._input, self._pos

        keyword_match = RE_KEYWORD.match(*match_args)
        if keyword_match:
            return unpack_match(keyword_match)

        symbol_match = RE_SYMBOL.match(*match_args)
        if symbol_match:
            jack_match = unpack_match(symbol_match)
            if jack_match.text == "<":
                return jack_match._replace(text="&lt;")
            elif jack_match.text == ">":
                return jack_match._replace(text="&gt;")
            elif jack_match.text == '"':
                return jack_match._replace("&quot;")
            elif jack_match.text == "&":
                return jack_match._replace("&amp;")
            else:
                return jack_match

        identifier_match = RE_IDENTIFIER.match(*match_args)
        if identifier_match:
            return unpack_match(identifier_match)

        int_match = RE_INT_CONST.match(*match_args)
        if int_match:
            return unpack_match(int_match)

        string_match = RE_STRING_CONST.match(*match_args)
        if string_match:
            jack_match = unpack_match(string_match)
            unquoted_string = jack_match.text.strip('"')
            return jack_match._replace(text=unquoted_string)

        if len(self._input[self._pos:].strip()) != 0:
            print("warning! failed to match string beginning '{}'".format(self._input[self._pos:self._pos+10]))


    @property
    def current_token(self):
        tokens = self.tokens.findall("*/.[last()]")
        if len(tokens) > 0:
            return tokens[-1]
        else:
            return None


    def has_more_tokens(self):
        """ Do we have more tokens in the input? """
        return self._lookahead() is not None

    def advance(self):
        """ Gets the next token from the input and makes it the current token. This method
        should only be called if hasMoreTokens() is true. Initially there is no current token. """
        jack_match = self._lookahead()
        if jack_match is not None:

            token_element = SubElement(self.tokens, jack_match.tag)
            token_element.text = jack_match.text
            self._pos += (jack_match.span.end - jack_match.span.start)
            return token_element

    def token_type(self):
        """ Returns the type of the current token - one of KEYWORD, SYMBOL, IDENTIFIER, INT_CONST, STRING_CONST """
        return self.current_token.tag

    def keyword(self):
        """ Returns the keyword which is the current token. Should be called only when tokenType() is KEYWORD

        Valid keywords: CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR, VOID, VAR, STATIC, FIELD, LET,
        DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS """
        assert self.token_type() == "KEYWORD", "called keyword() on token with type {}".format(self.token_type())
        return self.current_token.text

    def symbol(self):
        """ Returns the character which is the current token. Should be called only when tokenType() is SYMBOL

        returns: Char """
        assert self.token_type() == "SYMBOL", "called symbol() on token with type {}".format(self.token_type())
        return self.current_token.text

    def identifier(self):
        """Returns the identifier which is the current token. Should be called only when tokenType() is IDENTIFIER

        returns: String """
        assert self.token_type() == "IDENTIFIER", "called identifier() on token with type {}".format(self.token_type())
        return self.current_token.text

    def int_val(self):
        """ Returns the integer value of the current token. Should be called only when tokenType() is INT_CONST

        returns: Int """
        assert self.token_type() == "INT_CONST", "called int_val() on token with type {}".format(self.token_type())
        return int(self.current_token.text)

    def string_val(self):
        """Returns the string value of the current token, without the double quotes. Should be called only when
        tokenType() is STRING_CONST

        returns: String """
        assert self.token_type() == "STRING_CONST", "called string_val() on token with type {}".format(self.token_type())
        return self.current_token.text

class CompilationEngine():

    def __init__(self, jack_file_path, output_file_path):
        """ Creates a new compilation engine with the given input and output. The next routine called must be
        compile_class """
        self.jack_file_path = jack_file_path
        self.output_file_path = output_file_path
        pass

    def compile_class(self):
        """ Compiles a complete class """
        pass

    def compile_class_var_dec(self):
        """ Compiles a static variable declaration, or a field declaration """
        pass

    def compile_subroutine_dec(self):
        """ Compiles a complete method, function, or constructor """
        pass

    def compile_parameter_list(self):
        """ Compiles a (possibly empty) parameter list. Does not handle the enclosing '()' """
        pass

    def compile_subroutine_body(self):
        """ Compiles a subroutine's body """
        pass

    def compile_var_dec(self):
        """ Compiles a 'var' declaration """
        pass

    def compile_statements(self):
        """ Compiles a sequence of statements. Does not handle the enclosing '{}'

        Hint: Uses a loop to handle zero or more statement instances, according to the left-most token.
        If the left-most token is 'if', 'while'..., ...it invokes 'compile_if', 'compile_while', ....

        Note: There is no compile_statement method
        """
        pass

    def compile_let(self):
        """ Compiles a 'let' statement """
        pass

    def compile_if(self):
        """ Compiles an 'if' statement, possibly with a trailing 'else' clause """
        pass

    def compile_while(self):
        """ Compiles a 'while' statement """
        pass

    def compile_do(self):
        """ Compiles a 'do' statement """
        pass

    def compile_return(self):
        """ Compiles a 'return' statement """
        pass

    def compile_expression(self):
        """ Compiles an expression """
        pass

    def compile_term(self):
        """ Compiles a term

        If  the current token is a identifier, the routines must distinguish between a variable, an array entry, or a
        subroutine call. A single lookahead token (which may be one of '[', '(', or '.') suffices to distinguish
        between the possibilities. Any other token is not part of this term and should not be advanced over. """
        pass

    def compile_expressison_list(self):
        """ Compiles a (possibly empty) comma-separated list of expressions """
        pass



class TokenizerTest(unittest.TestCase):

    # Testing 'tokenize()'
    def tokenize(self, jack_snippet):
        tknzr = Tokenizer(jack_code=jack_snippet)
        xml = tknzr.tokenize()
        return [(child.tag, child.text) for child in xml]

    def test_call(self):
        jack_snippet = "point.getx()"
        actual = self.tokenize(jack_snippet)
        expected = [("IDENTIFIER", "point"), ("SYMBOL", "."), ("IDENTIFIER", "getx"), ("SYMBOL", "("), ("SYMBOL", ")")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_constant_let(self,):
        jack_snippet = "let x = 10"
        actual = self.tokenize(jack_snippet)
        expected = [("KEYWORD", "let"), ("IDENTIFIER", "x"), ("SYMBOL", "="), ("INT_CONST", "10")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_symbolic_let(self):
        jack_snippet = "var int g;"
        actual = self.tokenize(jack_snippet)
        expected = [("KEYWORD", "var"), ("KEYWORD", "int"), ("IDENTIFIER", "g"), ("SYMBOL", ";")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_return(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        actual = self.tokenize(jack_snippet)
        expected = [("KEYWORD", "return"), ("IDENTIFIER", "Fraction"), ("SYMBOL", "."), ("IDENTIFIER", "new"),
                    ("SYMBOL", "("), ("IDENTIFIER", "sum"), ("SYMBOL", ","), ("IDENTIFIER", "denominator"),
                    ("SYMBOL", "*"), ("IDENTIFIER", "other"), ("SYMBOL", "."), ("IDENTIFIER", "getDenominator"),
                    ("SYMBOL", "("), ("SYMBOL", ")"), ("SYMBOL", ")"), ("SYMBOL", ";")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_do(self):
        jack_snippet = 'do Output.printString("/");'
        actual = self.tokenize(jack_snippet)
        expected = [("KEYWORD", "do"), ("IDENTIFIER", "Output"), ("SYMBOL", "."), ("IDENTIFIER", "printString"),
                    ("SYMBOL", "("), ("STRING_CONST", '/'), ("SYMBOL", ")"), ("SYMBOL", ";")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))


    def test_constructor(self):
        jack_snippet = "constructor Fraction new(int x, int y) {"
        actual = self.tokenize(jack_snippet)
        expected = [("KEYWORD", "constructor"), ("IDENTIFIER", "Fraction"), ("IDENTIFIER", "new"), ("SYMBOL", "("),
            ("KEYWORD", "int"), ("IDENTIFIER", "x"), ("SYMBOL", ","), ("KEYWORD", "int"), ("IDENTIFIER", "y"),
            ("SYMBOL", ")"), ("SYMBOL", "{")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    def test_special_symbols(self):
        jack_snippet = "x > y; y < z"
        actual = self.tokenize(jack_snippet)
        expected = [("IDENTIFIER", "x"), ("SYMBOL", "&gt;"), ("IDENTIFIER", "y"), ("SYMBOL", ";"),
                    ("IDENTIFIER", "y"), ("SYMBOL", "&lt;"), ("IDENTIFIER", "z")]
        self.assertListEqual(actual, expected, "failed {}".format(jack_snippet))

    # Testing 'advance()'
    def test_advance_a(self):
        jack_snippet = "constructor Fraction new(int x, int y) {"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        tokenizer.advance()
        tokenizer.advance()
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(xml.text == "new", "advance() returned unexpected result: got '', expected 'new'".format(xml.text))

    def test_advance_b(self):
        jack_snippet = "return Fraction.new(sum, denominator * other.getDenominator());"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        for _ in range(10):
            tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(xml.text == "other", "advance() returned unexpected result: got '', expected 'other'".format(xml.text))

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
        self.assertTrue(xml.text == ";", "advance() returned unexpected result: got '', expected ';'".format(xml.text))
        tokenizer.advance()
        xml = tokenizer.current_token
        self.assertTrue(xml.text == ";", "advance() returned unexpected result: got '', expected ';'".format(xml.text))

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
        self.assertTrue(tokenizer.keyword() == "return", "Expected current_token to be of type 'keyword'")

    def test_int_val(self):
        jack_snippet = "return 12"
        tokenizer = Tokenizer(jack_code=jack_snippet)
        tokenizer.advance()
        tokenizer.advance()
        with self.assertRaises(AssertionError):
            tokenizer.keyword()
        self.assertTrue(tokenizer.int_val() == 12, "Expected current_token to be of type 'int_const'")


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

if __name__ == "__main__":
    unittest.main()

