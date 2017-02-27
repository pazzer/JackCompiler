__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
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
    #
    @staticmethod
    def _copy_element(element, parent):
        sub_element = ET.SubElement(parent, element.tag)
        sub_element.text = element.text
        return sub_element


    # def _insert_element(self, element, parent, advance=True):
    #     sub_element = ET.SubElement(parent, element.tag)
    #     sub_element.text = element.text
    #     if advance:
    #         self.tknzr.advance()
    #     return  sub_element

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

        # kw -> 'class'
        self._insert_current_token()

        # id -> 'className'
        self._insert_current_token()

        # symbol -> '{' (opens the class body)
        self._insert_current_token()

        # zero or more varDecs
        # ???

        # zero or more subroutineDecs
        self.compile_subroutine_dec()

        # symbol -> '}' (closes the class body)
        self._insert_current_token()

    @property
    def cur_tkn(self):
        return self.tknzr.current_token


    def compile_class_var_dec(self):
        """ Compiles a static variable declaration, or a field declaration """
        if self.cur_tkn.text not in ["static", "field"]:
            return

        # insert the 'classVarDec' node and add its kind (field|static)
        class_var_dec_node = ET.SubElement(self.current_node, "classVarDec")
        _ = self._copy_element(self.cur_tkn, parent=class_var_dec_node)
        self.tknzr.advance()

        # handling 'type'
        type_node = ET.SubElement(class_var_dec_node, 'type')
        parent_node = type_node
        if self.cur_tkn.text not in ["int", "char", "boolean"]:
            class_name_node = ET.SubElement(type_node, "className")
            parent_node = class_name_node
        _ = self._copy_element(self.cur_tkn, parent=parent_node)
        self.tknzr.advance()

        # handling one or more 'varName' declarations

        while True:
            # extract the variable name
            var_name_node = ET.SubElement(class_var_dec_node, 'varName')
            _ = self._copy_element(self.cur_tkn, parent=var_name_node)
            self.tknzr.advance()
            if self.cur_tkn.text == ",":
                # extract the delimiting comma
                _ = self._copy_element(self.cur_tkn, parent=class_var_dec_node)
                self.tknzr.advance()
            else:
                break

        # add the terminating ';'
        _ = self._copy_element(self.cur_tkn, parent=class_var_dec_node)
        self.tknzr.advance()


    def compile_subroutine_dec(self):
        """ Compiles a complete method, function, or constructor """
        parent_on_entry = self.current_node

        if self.cur_tkn.text not in [" constructor ", " function ", " method "]:
            return False

        subroutineDec = ET.SubElement(self.current_node, "subroutineDec")
        self.current_node = subroutineDec

        self._insert_current_token()
        self._insert_current_token()
        self._insert_current_token()
        self._insert_current_token()

        # now handle the parameter list
        self.compile_parameter_list()

        # eat the close-parent ')'
        assert self.cur_tkn.text == ' ) ', "expected ' ) ' got '{}'".format(self.cur_tkn.text)

        self._insert_current_token()

        self.compile_subroutine_body()

        self.current_node = parent_on_entry


    def compile_parameter_list(self):
        """ Compiles a (possibly empty) parameter list. Does not handle the enclosing '()' """
        parent_on_entry = self.current_node

        self.current_node = ET.SubElement(self.current_node, "parameterList")
        self.current_node.text = "\n"



        while True:

            if self.cur_tkn.text == " ) ":
                break

            # type
            self._insert_current_token()

            # varName
            _ = self._copy_element(self.cur_tkn, self.current_node)
            self.tknzr.advance()

            if self.cur_tkn.text == " , ":
                _ = self._copy_element(self.cur_tkn, self.current_node)
                self.tknzr.advance()

        self.current_node = parent_on_entry



    def compile_subroutine_body(self):
        """ Compiles a subroutine's body """
        assert self.cur_tkn.text == ' { ', "expected ' { ' got '{}'".format(self.cur_tkn.text)

        parent_on_entry = self.current_node
        self.current_node = ET.SubElement(self.current_node, 'subroutineBody')

        # opening '{'
        self._insert_current_token()


        self.compile_var_dec()


        self.compile_statements()

        # closing '}'
        self._insert_current_token()

        self.current_node = parent_on_entry


    def compile_var_dec(self):
        """ Compiles a 'var' declaration

        a 'varDec' element is only added if their is at least one variable declaration """
        if self.cur_tkn.text != " var ":
            return

        # adding 'varDec' node
        var_dec_node = ET.SubElement(self.current_node, "varDec")

        # adding 'var'
        _ = self._copy_element(self.cur_tkn, var_dec_node)
        self.tknzr.advance()

        # adding type
        _ = self._copy_element(self.cur_tkn, var_dec_node)
        self.tknzr.advance()

        while True:

            # adding name
            _ = self._copy_element(self.cur_tkn, var_dec_node)
            self.tknzr.advance()

            # adding ',' or ';'
            _ = self._copy_element(self.cur_tkn, var_dec_node)
            previous_token = self.cur_tkn
            self.tknzr.advance()

            if previous_token.text == " ; ":
                break


    def compile_statements(self):
        """ Compiles a sequence of statements. Does not handle the enclosing '{}'

        Hint: Uses a loop to handle zero or more statement instances, according to the left-most token.
        If the left-most token is 'if', 'while'..., ...it invokes 'compile_if', 'compile_while', ....

        Note: There is no compile_statement method
        """
        old_node = self.current_node
        self.current_node = ET.SubElement(self.current_node, 'statements')

        while self.cur_tkn.text in [" do ", " while ", " if ", " let ", " return "]:
            stmt_type = self.cur_tkn.text
            if stmt_type == " do ":
                self.compile_do()
            elif stmt_type == " while ":
                self.compile()
            elif stmt_type == " if ":
                self.compile_if()
            elif stmt_type == " let ":
                self.compile_let()
            elif stmt_type == " return ":
                self.compile_return()
            else:
                break

            #self.tknzr.advance()
        self.current_node = old_node


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
        stmts_node = self.current_node
        do_statement  = ET.SubElement(self.current_node, 'doStatement')
        self.current_node = do_statement

        # add 'do'
        _ = self._copy_element(self.cur_tkn, self.current_node)
        self.tknzr.advance()

        ## TRYING CALLING DIRECTLY INTO self.term to avoid replicating the code below.

        # add identifier (subroutineName, className, or varName)
        _ = self._copy_element(self.cur_tkn, self.current_node)
        self.tknzr.advance()

        if self.cur_tkn.text == " . ":
            # do xxx.xxx()
            _ = self._copy_element(self.cur_tkn, self.current_node)
            self.tknzr.advance()

            # eat subroutineName, and advance (to '(')
            _ = self._copy_element(self.cur_tkn, self.current_node)
            self.tknzr.advance()


        # eat the '(' and compile the expression list (if there is one)
        _ = self._copy_element(self.cur_tkn, self.current_node)
        self.tknzr.advance()
        self.compile_expressison_list()

        # eat the closing ')'
        _ = self._copy_element(self.cur_tkn, do_statement)
        self.tknzr.advance()

        # eat the terminating ';'
        _ = self._copy_element(self.cur_tkn, do_statement)
        self.tknzr.advance()
        self.current_node = stmts_node

    def compile_return(self):
        """ Compiles a 'return' statement """
        return_statement = ET.SubElement(self.current_node, 'returnStatement')
        _ = self._copy_element(self.cur_tkn, return_statement)
        self.tknzr.advance()

        if self.cur_tkn.text == " ; ":
            _ = self._copy_element(self.cur_tkn, return_statement)
        else:
            pass

        self.tknzr.advance()

    def compile_expression(self):
        """ Compiles an expression """

        self.current_node = ET.SubElement(self.current_node, 'expression')

        self.compile_term()


        while self.cur_tkn.text in [" + ", " - ", " * ", " / ", " & ", " | ", " < ", " > ", " = "]:
            _ = self._copy_element(self.cur_tkn, self.current_node)
            self.tknzr.advance()
            self.compile_term()



    def compile_term(self):
        """ Compiles a term

        If the current token is an identifier, the routines must distinguish between a variable, an array entry, or a
        subroutine call. A single lookahead token (which may be one of '[', '(', or '.') suffices to distinguish
        between the possibilities. Any other token is not part of this term and should not be advanced over. """
        term_node = ET.SubElement(self.current_node, 'term')
        tkn_tag = self.cur_tkn.tag
        tkn_txt = self.cur_tkn.text
        if tkn_tag in ["integerConstant", "keyword", "stringConstant"]:
            # term -> integerConstant | stringConstant | keywordConstant
            _ = self._copy_element(self.cur_tkn, term_node)
            self.tknzr.advance()

        elif tkn_txt in [" - ", " ~ "]:
            # term -> unaryOp term
            _ = self._copy_element(self.cur_tkn, term_node)
            self.tknzr.advance()
            self.compile_term()


        elif tkn_txt == " ( ":
            # term -> '(' expression ')'
            _ = self._copy_element(self.cur_tkn, term_node)
            self.tknzr.advance()
            old_node = self.current_node
            self.current_node = term_node
            self.compile_expression()
            self.current_node = term_node

            # consume the closing paren
            assert self.cur_tkn.text == " ) ", "wrong! current token is not closing paren ' ) '"
            _ = self._copy_element(self.cur_tkn, term_node)
            self.current_node = old_node
            self.tknzr.advance()

        elif tkn_tag == 'identifier':

            tkn_now = self.cur_tkn
            self.tknzr.advance()
            tkn_nxt = self.cur_tkn

            if tkn_nxt.text == ' [ ':
                # term -> varName '[' expresion ']'
                # tkn_now is a variable name, so add it, and add tkn_nxt ('[')
                _ = self._copy_element(tkn_now, term_node)  # identifier
                _ = self._copy_element(tkn_nxt, term_node)  # '['
                self.tknzr.advance()
                self.current_node = term_node
                self.compile_expression()
                self.current_node = term_node
                _ = self._copy_element(self.cur_tkn, term_node) # ']'
                self.tknzr.advance()


            elif tkn_nxt.text == ' ( ' or tkn_nxt.text == ' . ':

                _ = self._copy_element(tkn_now, term_node)  # identifier

                if self.cur_tkn.text == " . ":

                    _ = self._copy_element(self.cur_tkn, term_node)
                    self.tknzr.advance()

                    # eat subroutineName, and advance (to '(')
                    _ = self._copy_element(self.cur_tkn, term_node)
                    self.tknzr.advance()


                # eat the '(' and compile the expression list (if there is one)
                _ = self._copy_element(self.cur_tkn, term_node)
                self.tknzr.advance()
                self.current_node = term_node
                self.compile_expressison_list()

                # eat the closing ')'
                _ = self._copy_element(self.cur_tkn, term_node)
                self.tknzr.advance()


            else:
                # term -> varName
                #logging.warning("adding element: {}".format(tkn_now.text))
                _ = self._copy_element(tkn_now, term_node)


    def compile_expressison_list(self):
        """ Compiles a (possibly empty) comma-separated list of expressions """
        expression_list_node = ET.SubElement(self.current_node, 'expressionList')

        if self.cur_tkn.text == ' ) ':
            expression_list_node.text = "\n"
            # This is an expression-less expressionList
            return

        while True:
            self.current_node = expression_list_node
            self.compile_expression()

            if self.cur_tkn.text == ' , ':

                _ = self._copy_element(self.cur_tkn, expression_list_node)
                self.tknzr.advance()
            else:
                break


def stringify_xml(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="    ")
    return "\n".join(list(filter(lambda x: True if len(x.strip()) > 0 else False, pretty_string.split("\n"))))