__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
from xml.dom import minidom
import logging

class CompilationEngine():

    def __init__(self, tokenizer=None, output_file_path=None):
        """ Creates a new compilation engine with the given input and output. The next routine called must be
        compile_class """
        self.tknzr = tokenizer
        self.current_node = None
        self.xml_tree = ET.ElementTree()
        self.output_file_path = output_file_path
        self._stashed_parent = None

    def compile(self):
        self.tknzr.advance()
        self.compile_class()
        with open(self.output_file_path.as_posix(), "w") as outfile:
            outfile.write(stringify_xml(self.xml_tree.getroot()))

    @staticmethod
    def _copy_element(element, parent):
        sub_element = ET.SubElement(parent, element.tag)
        sub_element.text = element.text
        return sub_element

    def _insert_current_token(self, parent=None, advance=True):
        parent = self.current_node if parent is None else parent
        sub_element = ET.SubElement(parent, self.cur_tkn.tag)
        sub_element.text = self.cur_tkn.text
        if advance:
            self.tknzr.advance()

    def compile_class(self):
        """ Compiles a complete class

        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        if self.cur_tkn.text != " class ":
            return

        # add root node ('class')
        self.current_node = ET.Element("class")
        self.xml_tree._setroot(self.current_node)

        self._insert_current_token() # 'class'
        self._insert_current_token() # className
        self._insert_current_token() # '{'


        while self.cur_tkn.text in [" static ", " field "]:
            self.compile_class_var_dec()

        while self.cur_tkn.text in [" constructor ", " function ", " method "]:
            self.compile_subroutine_dec()

        self._insert_current_token() # '}'

    @property
    def cur_tkn(self):
        return self.tknzr.current_token

    def compile_class_var_dec(self):
        """ Compiles a static variable declaration, or a field declaration """
        if self.cur_tkn.text not in [" static ", " field "]:
            logging.warning(self.cur_tkn.text)
            return

        parent_node = self.current_node

        # insert the 'classVarDec' node and add its kind (field|static)
        self.current_node = ET.SubElement(self.current_node, "classVarDec")

        self._insert_current_token() # 'field' | 'static'
        self._insert_current_token() # type
        self._insert_current_token() # varName

        while self.cur_tkn.text == " , ":
                self._insert_current_token() # ' , '
                self._insert_current_token() # varName

        self._insert_current_token() # ' ; '

        self.current_node = parent_node

    def compile_subroutine_dec(self):
        """ Compiles a complete method, function, or constructor """
        if self.cur_tkn.text not in [" constructor ", " function ", " method "]:
            return False

        parent_on_entry = self.current_node

        self.current_node = ET.SubElement(self.current_node, "subroutineDec")

        self._insert_current_token() # 'constructor'|'function'|'method'
        self._insert_current_token() # 'void'|type
        self._insert_current_token() # subroutineName

        self._insert_current_token() # '('
        self.compile_parameter_list()
        self._insert_current_token() # ')'

        self.compile_subroutine_body()

        self.current_node = parent_on_entry

    def compile_parameter_list(self):
        """ Compiles a (possibly empty) parameter list. Does not handle the enclosing '()' """
        parent_on_entry = self.current_node

        self.current_node = ET.SubElement(self.current_node, "parameterList")
        self.current_node.text = "\n"

        while self.cur_tkn.text != " ) ":

            self._insert_current_token() # type (char, int, ...)
            self._insert_current_token() # varName

            if self.cur_tkn.text == " , ":
                self._insert_current_token() # ' , '

        self.current_node = parent_on_entry

    def compile_subroutine_body(self):
        """ Compiles a subroutine's body """
        assert self.cur_tkn.text == ' { ', "expected ' { ' got '{}'".format(self.cur_tkn.text)

        parent_on_entry = self.current_node
        self.current_node = ET.SubElement(self.current_node, 'subroutineBody')

        self._insert_current_token() # '{'

        while self.cur_tkn.text == " var ":
            self.compile_var_dec()

        self.compile_statements()
        self._insert_current_token() # '}'

        self.current_node = parent_on_entry

    def compile_var_dec(self):
        """ Compiles a 'var' declaration

        a 'varDec' element is only added if their is at least one variable declaration """
        if self.cur_tkn.text != " var ":
            return

        parent_on_entry = self.current_node

        # adding 'varDec' node
        self.current_node = ET.SubElement(self.current_node, "varDec")

        assert self.cur_tkn.text == ' var ', "expected ' var ', got ' {} '".format(self.cur_tkn.text)
        self._insert_current_token() # 'var'
        assert self.cur_tkn.tag in ['keyword', 'identifier'], "expected keyword or identifier, got ' {} '".format(self.cur_tkn.text)
        self._insert_current_token() # variable type (char, int...)

        while True:

            assert self.cur_tkn.tag == "identifier", "expected keyword or identifier, got ' {} '".format(self.cur_tkn.text)
            self._insert_current_token() # variable name

            # adding ',' or ';'
            previous_token = self.cur_tkn
            assert previous_token.text in [" ; ", " , "], "expected ' , ' or ' ; ', got {}".format(previous_token.text)
            self._insert_current_token()

            if previous_token.text == " ; ":
                break

        self.current_node = parent_on_entry

    def compile_statements(self):
        """ Compiles a sequence of statements. Does not handle the enclosing '{}'

        Hint: Uses a loop to handle zero or more statement instances, according to the left-most token.
        If the left-most token is 'if', 'while'..., ...it invokes 'compile_if', 'compile_while', ....

        Note: There is no compile_statement method
        """
        parent_on_entry = self.current_node
        self.current_node = ET.SubElement(self.current_node, 'statements')

        while self.cur_tkn.text in [" do ", " while ", " if ", " let ", " return "]:
            stmt_type = self.cur_tkn.text
            if stmt_type == " do ":
                self.compile_do()
            elif stmt_type == " while ":
                self.compile_while()
            elif stmt_type == " if ":
                self.compile_if()
            elif stmt_type == " let ":
                self.compile_let()
            elif stmt_type == " return ":
                self.compile_return()
            else:
                break

        self.current_node = parent_on_entry

    def compile_let(self):
        """ Compiles a 'let' statement """
        parent_node = self.current_node

        self.current_node = ET.SubElement(parent_node, "letStatement")

        assert self.cur_tkn.text == " let ", "expected 'let', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token()

        self._insert_current_token() # varName
        if self.cur_tkn.text == '[':
            self._insert_current_token() # ' [ '
            self.compile_expression()
            assert self.cur_tkn.text == ' ] ', "expected ']', got '{}'".format(self.cur_tkn.text)
            self._insert_current_token() # ' ] '

        assert self.cur_tkn.text == ' = ', "expected '=', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token() # ' = '
        self.compile_expression()

        assert self.cur_tkn.text == ' ; ', "expected ';', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token() # ' ; '

        self.current_node = parent_node

    def compile_if(self):
        """ Compiles an 'if' statement, possibly with a trailing 'else' clause """

        parent_node = self.current_node

        self.current_node = ET.SubElement(self.current_node, 'ifStatement')

        assert self.cur_tkn.text == ' if ', "expected 'if', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token() # 'if'

        assert self.cur_tkn.text == ' ( ', "expected '(', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token() # '('

        self.compile_expression()

        assert self.cur_tkn.text == ' ) ', "expected ')', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token() # ')'

        assert self.cur_tkn.text == ' { ', "expected '{', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token() # '{'

        self.compile_statements()

        assert self.cur_tkn.text == ' } ', "expected '}', got '{}'".format(self.cur_tkn.text)
        self._insert_current_token() # '}'

        if self.cur_tkn.text == ' else ':
            assert self.cur_tkn.text == ' { ', "expected '{', got '{}'".format(self.cur_tkn.text)
            self._insert_current_token() # '{'

            self.compile_statements()

            assert self.cur_tkn.text == ' } ', "expected '}', got '{}'".format(self.cur_tkn.text)
            self._insert_current_token() # '}'

        self.current_node = parent_node

    def compile_while(self):
        """ Compiles a 'while' statement """
        parent_node = self.current_node

        self.current_node = ET.SubElement(self.current_node, 'whileStatement')
        self._insert_current_token() # ' while '

        self._insert_current_token() # '('
        self.compile_expression()
        self._insert_current_token() # ')'

        self._insert_current_token() # '{'
        self.compile_statements()
        self._insert_current_token() # '}'

        self.current_node = parent_node

    def compile_do(self):
        """ Compiles a 'do' statement """
        parent_node = self.current_node

        self.current_node = ET.SubElement(self.current_node, 'doStatement')

        self._insert_current_token() # 'do'.
        self.compile_term() # term will 'expand' to 'subroutineCall'
        self._insert_current_token() # ';'

        self.current_node = parent_node

    def compile_return(self):
        """ Compiles a 'return' statement """
        parent_node = self.current_node

        self.current_node = ET.SubElement(self.current_node, 'returnStatement')
        self._insert_current_token()

        if self.cur_tkn.text != " ; ":
            self.compile_expression()

        self._insert_current_token()
        self.current_node = parent_node

    def compile_expression(self):
        """ Compiles an expression """
        parent_on_entry = self.current_node

        self.current_node = ET.SubElement(self.current_node, 'expression')
        self.compile_term()

        while self.cur_tkn.text in [" + ", " - ", " * ", " / ", " & ", " | ", " < ", " > ", " = "]:
            self._insert_current_token()
            self.compile_term()

        self.current_node = parent_on_entry

    def compile_term(self):
        """ Compiles a term

        If the current token is an identifier, the routines must distinguish between a variable, an array entry, or a
        subroutine call. A single lookahead token (which may be one of '[', '(', or '.') suffices to distinguish
        between the possibilities. Any other token is not part of this term and should not be advanced over. """
        parent_on_entry = self.current_node
        if self.current_node.tag != "doStatement":
            self.current_node = ET.SubElement(self.current_node, 'term')

        tkn_tag = self.cur_tkn.tag
        tkn_txt = self.cur_tkn.text

        if tkn_tag in ["integerConstant", "keyword", "stringConstant"]:
            # term -> integerConstant | stringConstant | keywordConstant
            self._insert_current_token()

        elif tkn_txt in [" - ", " ~ "]:
            # term -> unaryOp term
            self._insert_current_token()
            self.compile_term()

        elif tkn_txt == " ( ":
            # term -> '(' expression ')'
            self._insert_current_token() # '('
            self.compile_expression()
            self._insert_current_token() # ')'

        elif tkn_tag == 'identifier':
            # need to lookahead
            tkn_now = self.cur_tkn
            self.tknzr.advance()
            tkn_nxt = self.cur_tkn

            if tkn_nxt.text == ' [ ':
                # term -> varName '[' expresion ']'
                _ = self._copy_element(tkn_now, self.current_node)  # varName
                self._insert_current_token() # '['
                self.compile_expression()
                self._insert_current_token() # ']'

            elif tkn_nxt.text == ' ( ' or tkn_nxt.text == ' . ':
                _ = self._copy_element(tkn_now, self.current_node)  # identifier

                if self.cur_tkn.text == " . ":
                    self._insert_current_token() # '.'
                    self._insert_current_token() # subroutineName

                self._insert_current_token() # '( '
                self.compile_expressison_list()
                self._insert_current_token() # ')'

            else:
                # term -> varName
                _ = self._copy_element(tkn_now, self.current_node)

        self.current_node = parent_on_entry

    def compile_expressison_list(self):
        """ Compiles a (possibly empty) comma-separated list of expressions """
        expression_list_node = ET.SubElement(self.current_node, 'expressionList')

        if self.cur_tkn.text == ' ) ':
            expression_list_node.text = "\n"
            return

        parent_on_entry = self.current_node
        self.current_node = expression_list_node
        while True:

            self.compile_expression()

            if self.cur_tkn.text == ' , ':
                self._insert_current_token()
            else:
                break

        self.current_node = parent_on_entry



def stringify_xml(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="    ")
    return "\n".join(list(filter(lambda x: True if len(x.strip()) > 0 else False, pretty_string.split("\n"))))