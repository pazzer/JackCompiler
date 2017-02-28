__author__ = 'paulpatterson'

from collections import namedtuple
import re
import xml.etree.ElementTree as ET
import logging

SYMBOLS = "{ } ( ) [ ] . , ; + - * / & | < > = ~"
KEYWORDS = "class constructor function method field static var int char boolean void true false null this let do if \
else while return"

RE_KEYWORD = re.compile("(?:\s*)(?P<keyword>{})".format("|".join(KEYWORDS.split())))

ESCAPED_SYMBOLS= list(map(lambda x: '\\'+x, SYMBOLS.split()))
RE_SYMBOL = re.compile("(?:\s*)(?P<symbol>{})".format("|".join(ESCAPED_SYMBOLS)))

RE_INT_CONST = re.compile("(?:\s*)(?P<integerConstant>[0-9]+)")

RE_IDENTIFIER = re.compile("(?:\s*)(?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*)")

RE_STRING_CONST = re.compile("(?:\s*)(?P<stringConstant>\"[^\"\n]+\")")

RE_COMMENT = re.compile(r"""(?:\s*)/\*\*\n                  # /**
                            ([ ]\*[^/]*\n)+                 #  * lorem ipsum...
                            [ ]+\*/                         #  */
                            |
                            (?:\s*)/\*\*[^\*]+\*/           # /** lorem ipsum... */
                            |
                            (?:\s*)//[^\n]*""", re.VERBOSE) # // lorem ipsum...

Span = namedtuple("Span", "start end")
JackMatch = namedtuple("JackMatch", "tag text span")

class Tokenizer():

    def __init__(self, jack_code=None, jack_filepath=None):
        """ Opens the input file/stream and gets ready to tokenize it. """
        if jack_filepath is not None:
            with open(jack_filepath.as_posix(), 'r') as jack_file:
                self._input = jack_file.read()
        else:
            self._input = jack_code
        self.tokens = ET.Element("tokens")
        self._pos = 0
        #logging.warning(self._input)


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

            assert len(group_names) in [1,0], \
                "Expected one named group, but got {} ({})".format(len(group_names), group_names)

            if len(group_names) == 0:
                tag = "comment"
                text = ""
            else:
                tag = group_names[0]
                text = token_match.groups(tag)[0]
            return JackMatch(tag, text, span)

        match_args = self._input, self._pos

        comment_match = RE_COMMENT.match(*match_args)
        while comment_match is not None:
            unpacked = unpack_match(comment_match)
            self._pos = unpacked.span.end
            match_args = self._input, self._pos
            comment_match = RE_COMMENT.match(*match_args)

        if comment_match:
            return unpack_match(comment_match)

        keyword_match = RE_KEYWORD.match(*match_args)
        if keyword_match:
            return unpack_match(keyword_match)

        symbol_match = RE_SYMBOL.match(*match_args)
        if symbol_match:
            return unpack_match(symbol_match)

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
            token_element = ET.SubElement(self.tokens, jack_match.tag)
            token_element.text = " {} ".format(jack_match.text)
            self._pos = jack_match.span.end
            return token_element

    def token_type(self):
        """ Returns the type of the current token: keyword, symbol, identifer, integerConstant, or stringConstant """
        return self.current_token.tag

    def keyword(self):
        """ Returns the keyword which is the current token. Should be called only when tokenType() is keyword

        Valid keywords: CLASS, METHOD, FUNCTION, CONSTRUCTOR, INT, BOOLEAN, CHAR, VOID, VAR, STATIC, FIELD, LET,
        DO, IF, ELSE, WHILE, RETURN, TRUE, FALSE, NULL, THIS """
        assert self.token_type() == "keyword", "called keyword() on token with type {}".format(self.token_type())
        return self.current_token.text

    def symbol(self):
        """ Returns the character which is the current token. Should be called only when tokenType() is symbol

        returns: Char """
        assert self.token_type() == "symbol", "called symbol() on token with type {}".format(self.token_type())
        return self.current_token.text

    def identifier(self):
        """Returns the identifier which is the current token. Should be called only when tokenType() is IDENTIFIER

        returns: String """
        assert self.token_type() == "identifier", "called identifier() on token with type {}".format(self.token_type())
        return self.current_token.text

    def int_val(self):
        """ Returns the integer value of the current token. Should be called only when tokenType() is integerConstant

        returns: Int """
        assert self.token_type() == "integerConstant", "called int_val() on token with type {}".format(self.token_type())
        return int(self.current_token.text)

    def string_val(self):
        """Returns the string value of the current token, without the double quotes. Should be called only when
        tokenType() is stringConstant

        returns: String """
        assert self.token_type() == "stringConstant", "called string_val() on token with type {}".format(self.token_type())
        return self.current_token.text

    def __str__(self):
        return "\n".join(["{}, {}".format(child.tag, child.text) for child in self.tokens])
