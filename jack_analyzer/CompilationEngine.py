__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from functools import wraps
import sys

OPERATORS = [" + ", " - ", " * ", " / ", " & ", " | ", " < ", " > ", " = "]

TYPE_PATTERN = r" int | char | boolean | [a-zA-Z_][a-zA-Z0-9_]* "


def record_parent(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        compilation_engine = args[0]
        compilation_engine.node_ancestors.append(compilation_engine.current_node)
        return func(*args, **kwargs)
    return func_wrapper


def reinstate_parent(func):
    @wraps(func)
    def func_wrapper(*args, **kwargs):
        compilation_engine = args[0]
        retval = func(*args, **kwargs)
        compilation_engine.current_node = compilation_engine.node_ancestors.pop()
        return retval
    return func_wrapper


class CompilationEngine():

    def __init__(self, tokenizer=None, output_file_path=None):
        """ Creates a new compilation engine with the given input and output. The next routine called must be
        compile_class """
        self.tknzr = tokenizer
        self.current_node = None
        self.node_ancestors = []
        self.xml_tree = ET.ElementTree()
        self.output_file_path = output_file_path

    @property
    def cur_tkn(self):
        return self.tknzr.current_token

    # @property
    # def parent_node(self):
    #     self.xml_tree.find()

    def compile(self):
        self.tknzr.advance()
        self._compile_class()
        out_string = stringify_xml(self.xml_tree.getroot())
        if self.output_file_path is None:
            sys.stdout.write(out_string)
        else:
            with open(self.output_file_path.as_posix(), "w") as outfile:
                outfile.write(out_string)

    def _compile_class(self):
        """ Compiles a complete class

        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        if self.cur_tkn.text != " class ":
            return

        self.current_node = ET.Element("class")
        self.xml_tree._setroot(self.current_node)

        self._eat_keyword("class")
        self._eat_identifier()
        self._eat_symbol("{")

        while self.cur_tkn.text in [" static ", " field "]:
            self._compile_class_var_dec()

        while self.cur_tkn.text in [" constructor ", " function ", " method "]:
            self._compile_subroutine_dec()

        self._eat_symbol("}")

    @record_parent
    @reinstate_parent
    def _compile_class_var_dec(self):
        """ Compiles a static variable declaration, or a field declaration """
        if self.cur_tkn.text not in [" static ", " field "]:
            return

        self.current_node = ET.SubElement(self.current_node, "classVarDec")

        self._eat_keyword(["field", "static"])
        self._eat(expected_pattern=TYPE_PATTERN)
        self._eat_identifier()  # varName

        while self.cur_tkn.text == " , ":
                self._eat_symbol(",")
                self._eat_identifier()  # varName

        self._eat_symbol(";")

    @record_parent
    @reinstate_parent
    def _compile_subroutine_dec(self):
        """ Compiles a complete method, function, or constructor """
        if self.cur_tkn.text not in [" constructor ", " function ", " method "]:
            return False

        self.current_node = ET.SubElement(self.current_node, "subroutineDec")

        self._eat_keyword(["constructor", "function", "method"])
        self._eat(expected_pattern=TYPE_PATTERN + "| void ")
        self._eat_identifier()  # subroutineName

        self._eat_symbol("(")
        self._compile_parameter_list()
        self._eat_symbol(")")

        self._compile_subroutine_body()

    @record_parent
    @reinstate_parent
    def _compile_parameter_list(self):
        """ Compiles a (possibly empty) parameter list. Does not handle the enclosing '()' """
        self.current_node = ET.SubElement(self.current_node, "parameterList")
        self.current_node.text = "\n"

        while self.cur_tkn.text != " ) ":

            self._eat(expected_pattern=TYPE_PATTERN)
            self._eat_identifier()  # varName

            if self.cur_tkn.text == " , ":
                self._eat_symbol(",")

    @record_parent
    @reinstate_parent
    def _compile_subroutine_body(self):
        """ Compiles a subroutine's body """
        self.current_node = ET.SubElement(self.current_node, 'subroutineBody')

        self._eat_symbol("{")
        while self.cur_tkn.text == " var ":
            self._compile_var_dec()

        self._compile_statements()
        self._eat_symbol("}")

    @record_parent
    @reinstate_parent
    def _compile_var_dec(self):
        """ Compiles a 'var' declaration

        a 'varDec' element is only added if their is at least one variable declaration """
        if self.cur_tkn.text != " var ":
            return

        self.current_node = ET.SubElement(self.current_node, "varDec")

        self._eat_keyword("var")
        self._eat(expected_pattern=TYPE_PATTERN)

        while True:

            assert self.cur_tkn.tag == "identifier", \
                "expected keyword or identifier, got ' {} '".format(self.cur_tkn.text)
            self._eat_identifier()  # variable name

            previous_token = self.cur_tkn
            self._eat_symbol([";", ","])

            if previous_token.text == " ; ":
                break

    @record_parent
    @reinstate_parent
    def _compile_statements(self):
        """ Compiles a sequence of statements. Does not handle the enclosing '{}'

        Hint: Uses a loop to handle zero or more statement instances, according to the left-most token.
        If the left-most token is 'if', 'while'..., ...it invokes 'compile_if', 'compile_while', ....

        Note: There is no compile_statement method
        """
        self.current_node = ET.SubElement(self.current_node, 'statements')

        while self.cur_tkn.text in [" do ", " while ", " if ", " let ", " return "]:
            stmt_type = self.cur_tkn.text
            if stmt_type == " do ":
                self._compile_do()
            elif stmt_type == " while ":
                self._compile_while()
            elif stmt_type == " if ":
                self._compile_if()
            elif stmt_type == " let ":
                self._compile_let()
            elif stmt_type == " return ":
                self._compile_return()
            else:
                break

    @record_parent
    @reinstate_parent
    def _compile_let(self):
        """ Compiles a 'let' statement """
        self.current_node = ET.SubElement(self.current_node, "letStatement")

        self._eat_keyword("let")
        self._eat_identifier()  # varName

        if self.cur_tkn.text == ' [ ':
            self._eat_symbol("[")
            self._compile_expression()
            self._eat_symbol("]")

        self._eat_symbol("=")
        self._compile_expression()
        self._eat_symbol(";")

    @record_parent
    @reinstate_parent
    def _compile_if(self):
        """ Compiles an 'if' statement, possibly with a trailing 'else' clause """
        self.current_node = ET.SubElement(self.current_node, 'ifStatement')

        self._eat_keyword("if")
        self._eat_symbol("(")
        self._compile_expression()
        self._eat_symbol(")")

        self._eat_symbol("{")
        self._compile_statements()
        self._eat_symbol("}")

        if self.cur_tkn.text == ' else ':
            self._eat_keyword("else")
            self._eat_symbol("{")
            self._compile_statements()
            self._eat_symbol("}")

    @record_parent
    @reinstate_parent
    def _compile_while(self):
        """ Compiles a 'while' statement """
        self.current_node = ET.SubElement(self.current_node, 'whileStatement')

        self._eat_keyword("while")
        self._eat_symbol("(")
        self._compile_expression()
        self._eat_symbol(")")

        self._eat_symbol("{")
        self._compile_statements()
        self._eat_symbol("}")

    @record_parent
    @reinstate_parent
    def _compile_do(self):
        """ Compiles a 'do' statement """
        self.current_node = ET.SubElement(self.current_node, 'doStatement')

        self._eat_keyword("do")
        self._compile_term()  # term will 'expand' to 'subroutineCall'
        self._eat_symbol(";")

    @record_parent
    @reinstate_parent
    def _compile_return(self):
        """ Compiles a 'return' statement """

        self.current_node = ET.SubElement(self.current_node, 'returnStatement')
        self._eat_keyword("return")

        if self.cur_tkn.text != " ; ":
            self._compile_expression()

        self._eat_symbol(";")

    @record_parent
    @reinstate_parent
    def _compile_expression(self):
        """ Compiles an expression """

        self.current_node = ET.SubElement(self.current_node, 'expression')
        self._compile_term()

        while self.cur_tkn.text in OPERATORS:
            self._eat_symbol()
            self._compile_term()

    @record_parent
    @reinstate_parent
    def _compile_term(self):
        """ Compiles a term

        If the current token is an identifier, the routines must distinguish between a variable, an array entry, or a
        subroutine call. A single lookahead token (which may be one of '[', '(', or '.') suffices to distinguish
        between the possibilities. Any other token is not part of this term and should not be advanced over. """
        if self.current_node.tag != "doStatement":
            self.current_node = ET.SubElement(self.current_node, 'term')

        tkn_tag = self.cur_tkn.tag
        tkn_txt = self.cur_tkn.text

        if tkn_tag in ["integerConstant", "keyword", "stringConstant"]:
            # term -> integerConstant | stringConstant | keywordConstant
            self._eat()

        elif tkn_txt in [" - ", " ~ "]:
            # term -> unaryOp term
            self._eat_symbol()
            self._compile_term()

        elif tkn_txt == " ( ":
            self._eat_symbol("(")
            self._compile_expression()
            self._eat_symbol(")")

        elif tkn_tag == 'identifier':
            # need to lookahead
            self._eat_identifier()
            tkn_nxt = self.cur_tkn

            if tkn_nxt.text == ' [ ':
                self._eat_symbol("[")
                self._compile_expression()
                self._eat_symbol("]")

            elif tkn_nxt.text == ' ( ' or tkn_nxt.text == ' . ':

                if self.cur_tkn.text == " . ":
                    self._eat_symbol(".")
                    self._eat_identifier()  # subroutineName

                self._eat_symbol("(")
                self._compile_expressison_list()
                self._eat_symbol(")")

    @record_parent
    @reinstate_parent
    def _compile_expressison_list(self):
        """ Compiles a (possibly empty) comma-separated list of expressions """
        expression_list_node = ET.SubElement(self.current_node, 'expressionList')

        if self.cur_tkn.text == ' ) ':
            expression_list_node.text = "\n"
            return

        self.current_node = expression_list_node
        while True:

            self._compile_expression()

            if self.cur_tkn.text != ' , ':
                break

            self._eat_symbol(",")

    # Consuming tokens

    def _eat_symbol(self, expected_value=None):
        self._validate_and_insert_current_token("symbol", expected_value)

    def _eat_identifier(self, expected_value=None):
        self._validate_and_insert_current_token("identifier", expected_value)

    def _eat_string_constant(self, expected_value=None):
        self._validate_and_insert_current_token("stringConstant", expected_value)

    def _eat_integer_constant(self, expected_value=None):
        self._validate_and_insert_current_token("integerConstant", expected_value)

    def _eat_keyword(self, expected_value=None):
        self._validate_and_insert_current_token("keyword", expected_value)

    def _eat(self, expected_value=None, expected_pattern=None):
        self._validate_and_insert_current_token(expected_value=expected_value, expected_pattern=expected_pattern)

    def _validate_and_insert_current_token(self, expected_type=None, expected_value=None, expected_pattern=None):
        tkn_type = self.cur_tkn.tag
        tkn_text = self.cur_tkn.text
        if expected_type is not None:
            assert tkn_type == expected_type, \
                "unexpected token type; type of current token is '{}', not '{}'".format(tkn_type, expected_type)
        if expected_value is not None:
            try:
                assert tkn_text == " " + expected_value + " ", \
                    "unexpected value; value of current token is '{}' not '{}'".format(tkn_text, expected_value)
            except TypeError:
                assert tkn_text in [" " + v + " " for v in expected_value], \
                    "unexpected value; value of current token '{}' is not in '{}'".format(tkn_text, expected_value)
        if expected_pattern is not None:
            regex = re.compile(expected_pattern)
            assert regex.search(tkn_text) is not None, \
                "expected current token value to match pattern {}; it didn't.".format(expected_pattern)

        sub_element = ET.SubElement(self.current_node, self.cur_tkn.tag)
        sub_element.text = self.cur_tkn.text
        self.tknzr.advance()

def stringify_xml(elem):
    """ Return a pretty-printed XML string for the Element. """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="    ")
    return "\n".join(list(filter(lambda x: True if len(x.strip()) > 0 else False, pretty_string.split("\n"))))