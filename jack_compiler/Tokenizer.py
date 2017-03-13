__author__ = 'paulpatterson'

from collections import namedtuple
import re
import xml.etree.ElementTree as ET

SYMBOLS = "{ } ( ) [ ] . , ; + - * / & | < > = ~"
KEYWORDS = "class constructor function method field static var int char boolean void true false null this let do if \
else while return"

RE_KEYWORD = re.compile("(?:\s*)(?P<keyword>{})(?![A-Za-z_])".format("|".join(KEYWORDS.split())))

ESCAPED_SYMBOLS= list(map(lambda x: '\\'+x, SYMBOLS.split()))
RE_SYMBOL = re.compile("(?:\s*)(?P<symbol>{})".format("|".join(ESCAPED_SYMBOLS)))

RE_INT_CONST = re.compile("(?:\s*)(?P<integerConstant>[0-9]+)")

RE_IDENTIFIER = re.compile("(?:\s*)(?P<identifier>[a-zA-Z_][a-zA-Z0-9_]*)")

RE_STRING_CONST = re.compile("(?:\s*)(?P<stringConstant>\"[^\"\n]+\")")

RE_COMMENT = re.compile(r"""(?:\s*)/\*\*.*?\*/                          # /** lorem ipsum... */
                            |
                            (?:\s*)//[^\n]+""", re.VERBOSE | re.DOTALL) # // lorem ipsum...

Span = namedtuple("Span", "start end")
JackMatch = namedtuple("JackMatch", "tag text span")


class Tokenizer():

    def __init__(self, jack_filepath):
        """ Creates a Tokenizer, ready to tokenize a jack string or a jack file.

        Exactly one argument is expected; if two are received the file path argument is used to create the Tokenizer's
        input, and the jack_code argument is ignored.

        :param jack_code: a string representing error-free .jack code
        :type jack_code: str
        :param jack_filepath: a pathlib.Path object representing an error-free .jack file
        :type jack_filepath: pathlib.Path
         """
        with open(jack_filepath.as_posix(), 'r') as jack_file:
            self._input = jack_file.read()

        self.tokens = ET.Element("tokens")
        self._pos = 0


    def tokenize(self):
        """ Tokenizes the entire input string in one go (useful for testing).

         Marches through the input until the last token is consumed, at which point all identified tokens are returned
         in the form of a simple xml object; the root node of this object has the tag 'tokens' and its children are
         childless elements each of which represent one token. The tag of each token denotes the token type (one of
         (symbol, identifier, stringConstant, integerConstant, keyword), whilst the 'text' attribute stores the token's
         value
         """
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
        """
        Returns the current token in the form of an xml element.

        Use the 'tag' and 'text' properties of this element to return the token's type and value respectively.
        """
        tokens = self.tokens.findall("*/.[last()]")
        if len(tokens) > 0:
            return tokens[-1]
        else:
            return None

    def advance(self):
        """ Gets the next token from the input and makes it the current token. Initially there is no current token. """
        jack_match = self._lookahead()
        if jack_match is not None:
            token_element = ET.SubElement(self.tokens, jack_match.tag)
            token_element.text = " {} ".format(jack_match.text)
            self._pos = jack_match.span.end
            return token_element

    def __str__(self):
        """ Outputs the type and value of all tokens processed so far. """
        Tokenizer()
        return "\n".join(["{}, {}".format(child.tag, child.text) for child in self.tokens])
