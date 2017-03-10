__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
from functools import wraps
import sys
from jack_analyzer.SymbolTable import SymbolTable
import logging as log

OPERATORS = [" + ", " - ", " * ", " / ", " & ", " | ", " < ", " > ", " = "]

JACK_ARITHMETIC_COMMANDS = [" + ", " - ", " * ", " / ", " & ", " | ", " = ", " > ", " < "]
BUILT_IN_TYPES = ["int", "char", "boolean"]
TYPE_PATTERN = r" int | char | boolean | [a-zA-Z_][a-zA-Z0-9_]* "


class SubroutineSummary():
    def __init__(self):
        self.class_name = None
        self.name = None
        self.num_params = None
        self.num_locals = None
        self.kind = None

    def is_method(self):
        return self.kind == "method"

    def is_constructor(self):
        return self.kind== "constructor"

    def is_subroutine(self):
        return self.kind == "subroutine"

    def update(self, class_name=None, name=None, num_params=None, num_locals=None, kind=None):
        if class_name is not None:
            self.class_name = class_name
        if name is not None:
            self.name = name
        if num_params is not None:
            self.num_params = num_params
        if num_locals is not None:
            self.num_locals = num_locals
        if kind is not None:
            self.kind = kind

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

    def __init__(self, tokenizer=None, vm_writer=None):
        """ Creates a new compilation engine with the given input and output. The next routine called must be
        compile_class """
        self.tknzr = tokenizer
        self.vm_writer = vm_writer
        self.symbol_table = SymbolTable()
        self.node_ancestors = []
        self.parse_tree = ET.ElementTree()

        self.subroutine_summary = SubroutineSummary()
        self.current_node = None
        self.class_name = None
        self.subroutine_name = None
        self.subroutine_is_method = False

        self.compiling_let = False
        self.compiling_do = False

        self.if_counter = None
        self.while_counter = None


    @property
    def cur_tkn(self):
        return self.tknzr.current_token

    def write_parse_tree(self):
        root = self.parse_tree.getroot()
        pretty_xml = stringify_xml(root)
        sys.stdout.write(pretty_xml)

    def compile(self):
        self.tknzr.advance()
        self._compile_class()

    def _compile_class(self):
        """ Compiles a complete class

        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """

        if self.cur_tkn.text != " class ":
            return

        self.current_node = ET.Element("class")
        self.parse_tree._setroot(self.current_node)

        self._eat_keyword("class")
        self.class_name = self._eat_identifier()
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
        field_or_static = self._eat_keyword()
        var_type = self._eat(expected_pattern=TYPE_PATTERN)
        var_name = self._eat_identifier()
        self.symbol_table.define(var_name, var_type, field_or_static.upper())

        while self.cur_tkn.text == " , ":
            self._eat_symbol(",")
            var_name = self._eat_identifier()
            self.symbol_table.define(var_name, var_type, field_or_static.upper())

        self._eat_symbol(";")

    @record_parent
    @reinstate_parent
    def _compile_subroutine_dec(self):
        """ Compiles a complete method, function, or constructor """
        if self.cur_tkn.text not in [" constructor ", " function ", " method "]:
            return False

        self.subroutine_summary.update(kind=self.cur_tkn.text.strip(), class_name=self.class_name)

        self.symbol_table.start_subroutine()
        self.subroutine_is_method = self.cur_tkn.text == " method "
        self.current_node = ET.SubElement(self.current_node, "subroutineDec")

        # if self.cur_tkn.text == " constructor ":


        if self._eat_keyword() == "method":
            self.symbol_table.define("this", self.class_name, "ARG")
        self._eat()
        self.subroutine_name = self._eat_identifier()

        self._eat_symbol("(")
        self._compile_parameter_list() # Only adds to symbol table
        self._eat_symbol(")")

        self._compile_subroutine_body()
        self.subroutine_name = None


    @record_parent
    @reinstate_parent
    def _compile_parameter_list(self):
        """ Compiles a (possibly empty) parameter list. Does not handle the enclosing '()' """
        self.current_node = ET.SubElement(self.current_node, "parameterList")
        self.current_node.text = "\n"
        num_params = 0
        while self.cur_tkn.text != " ) ":

            var_type = self._eat(expected_pattern=TYPE_PATTERN)
            var_name = self._eat_identifier()  # varName
            self.symbol_table.define(var_name, var_type, "ARG")
            num_params += 1

            if self.cur_tkn.text == " , ":
                _ = self._eat_symbol(",")

        self.subroutine_summary.update(num_params=num_params)


    @record_parent
    @reinstate_parent
    def _compile_subroutine_body(self):
        """ Compiles a subroutine's body """

        self.if_counter = 0
        self.while_counter = 0
        self.current_node = ET.SubElement(self.current_node, 'subroutineBody')

        self._eat_symbol("{")

        while self.cur_tkn.text == " var ":
            self._compile_var_dec()

        ## Write the signature
        func_name = "{}.{}".format(self.class_name, self.subroutine_name)
        self.vm_writer.write_function(func_name, self.symbol_table.var_count("VAR"))

        if self.subroutine_summary.is_constructor():
            self.vm_writer.write_push("CONST", self.symbol_table.var_count("FIELD"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif self.subroutine_summary.is_method():
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)

        self._compile_statements()
        self._eat_symbol("}")
        self.if_counter = 0

    @record_parent
    @reinstate_parent
    def _compile_var_dec(self):
        """ Compiles a 'var' declaration

        a 'varDec' element is only added if their is at least one variable declaration """
        if self.cur_tkn.text != " var ":
            return

        self.current_node = ET.SubElement(self.current_node, "varDec")

        self._eat_keyword("var")
        var_type = self._eat(expected_pattern=TYPE_PATTERN)

        while True:

            assert self.cur_tkn.tag == "identifier", \
                "expected keyword or identifier, got ' {} '".format(self.cur_tkn.text)
            var_name = self._eat_identifier()  # variable name
            self.symbol_table.define(var_name, var_type, "VAR")

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
                self.compiling_do = True
                self._compile_do()
                self.compiling_do = False
            elif stmt_type == " while ":
                self._compile_while()
            elif stmt_type == " if ":
                self._compile_if()
            elif stmt_type == " let ":
                self.compiling_let = True
                self._compile_let()
                self.compiling_let = False
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
        var_name = self._eat_identifier()

        array_assignment = False

        if self.cur_tkn.text == ' [ ':
            array_assignment = True

            self._eat_symbol("[")
            self._compile_expression()
            symbol_kind = self.symbol_table.kind_of(var_name)
            symbol_index = self.symbol_table.index_of(var_name)
            self.vm_writer.write_push(symbol_kind, symbol_index)
            self.vm_writer.write_arithmetic("ADD")
            self._eat_symbol("]")

        self._eat_symbol("=")
        self._compile_expression()

        if array_assignment:
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)

        self._eat_symbol(";")

        if self.symbol_table.recognises_symbol(var_name) and not array_assignment:
            kind = self.symbol_table.kind_of(var_name)
            index = self.symbol_table.index_of(var_name)
            self.vm_writer.write_pop(kind, index)


    @record_parent
    @reinstate_parent
    def _compile_if(self):
        """ Compiles an 'if' statement, possibly with a trailing 'else' clause """
        self.current_node = ET.SubElement(self.current_node, 'ifStatement')
        label_suffix = self.if_counter
        self.if_counter += 1
        self._eat_keyword("if")
        self._eat_symbol("(")
        self._compile_expression()
        self._eat_symbol(")")

        self.vm_writer.write_if_goto("IF_TRUE{}".format(label_suffix))
        self.vm_writer.write_goto("IF_FALSE{}".format(label_suffix))
        self.vm_writer.write_label("IF_TRUE{}".format(label_suffix))

        self._eat_symbol("{")
        self._compile_statements()
        self._eat_symbol("}")

        if self.cur_tkn.text == ' else ':
            self.vm_writer.write_goto("IF_END{}".format(label_suffix))

        self.vm_writer.write_label("IF_FALSE{}".format(label_suffix))

        if self.cur_tkn.text == ' else ':

            self._eat_keyword("else")
            self._eat_symbol("{")
            self._compile_statements()
            self._eat_symbol("}")
            self.vm_writer.write_label("IF_END{}".format(label_suffix))


    @record_parent
    @reinstate_parent
    def _compile_while(self):
        """ Compiles a 'while' statement """
        self.current_node = ET.SubElement(self.current_node, 'whileStatement')
        label_suffix = self.while_counter
        self.while_counter += 1
        self.vm_writer.write_label("WHILE_EXP{}".format(label_suffix))

        self._eat_keyword("while")
        self._eat_symbol("(")
        self._compile_expression()
        self._eat_symbol(")")

        self.vm_writer.write_arithmetic("NOT")
        self.vm_writer.write_if_goto("WHILE_END{}".format(label_suffix))

        self._eat_symbol("{")
        self._compile_statements()
        self._eat_symbol("}")

        self.vm_writer.write_goto("WHILE_EXP{}".format(label_suffix))
        self.vm_writer.write_label("WHILE_END{}".format(label_suffix))

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
        else:
            self.vm_writer.write_push("CONST", 0)

        self.vm_writer.write_return()
        self._eat_symbol(";")

    @record_parent
    @reinstate_parent
    def _compile_expression(self):
        """ Compiles an expression """

        self.current_node = ET.SubElement(self.current_node, 'expression')
        self._compile_term()

        while self.cur_tkn.text in OPERATORS:
            command = self._eat_symbol()
            self._compile_term()
            if command == "+":
                self.vm_writer.write_arithmetic("ADD")
            elif command == "|":
                self.vm_writer.write_arithmetic("OR")
            elif command == "-":
                self.vm_writer.write_arithmetic("SUB")
            elif command == "=":
                self.vm_writer.write_arithmetic("EQ")
            elif command == ">":
                self.vm_writer.write_arithmetic("GT")
            elif command == "<":
                self.vm_writer.write_arithmetic("LT")
            elif command == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            elif command == "&":
                self.vm_writer.write_arithmetic("AND")
            elif command == "/":
                self.vm_writer.write_call("Math.divide", 2)





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

            value = self._eat()
            if tkn_tag == "integerConstant":
                self.vm_writer.write_push("CONST", value)
            elif tkn_tag == "stringConstant":
                self.vm_writer.write_string(tkn_txt)
            elif tkn_txt == " true ":
                self.vm_writer.write_push("CONST", 0)
                self.vm_writer.write_arithmetic("NOT")
            elif tkn_txt in [" false ", " null "]:
                self.vm_writer.write_push("CONST", 0)
            elif tkn_txt == " this ":
                self.vm_writer.write_push("POINTER", 0)
            else:
                pass

        elif tkn_txt in [" - ", " ~ "]:
            # term -> unaryOp term
            command = "NEG" if self._eat_symbol() == "-" else "NOT"
            self._compile_term()
            self.vm_writer.write_arithmetic(command)

        elif tkn_txt == " ( ":
            # term -> '(' expression ')'
            self._eat_symbol("(")
            self._compile_expression()
            self._eat_symbol(")")

        elif tkn_tag == 'identifier':
            # need to lookahead
            identifier = self._eat_identifier()
            tkn_nxt = self.cur_tkn

            if tkn_nxt.text == ' [ ':
                # term -> varName '[' expression ']'
                variable = identifier
                self._eat_symbol("[")
                self._compile_expression()
                self.vm_writer.write_push(self.symbol_table.kind_of(variable), self.symbol_table.index_of(variable))
                self.vm_writer.write_arithmetic("ADD")
                self.vm_writer.write_pop("POINTER", 1)
                self.vm_writer.write_push("THAT", 0)
                self._eat_symbol("]")

            elif tkn_nxt.text == ' ( ' or tkn_nxt.text == ' . ':
                num_args = 0
                self.calling_method = False
                if self.cur_tkn.text == " . ":
                    self._eat_symbol(".")
                    subroutine_name = self._eat_identifier().strip()

                    if self.symbol_table.recognises_symbol(tkn_txt.strip()):
                        # term -> varName '.' subroutineName '(' expressionList ')'
                        # tkn_text is a varName
                        # (a METHOD call)
                        # .jack: do game.run()
                        # .vm:   function PongGame.run 1 // 1 arg (self)

                        symbol_type = self.symbol_table.type_of(tkn_txt.strip())
                        symbol_index = self.symbol_table.index_of(tkn_txt.strip())
                        symbol_kind = self.symbol_table.kind_of(tkn_txt.strip())
                        #if symbol_type not in BUILT_IN_TYPES:
                        self.vm_writer.write_push(symbol_kind, symbol_index)
                        call_name = symbol_type + "." + subroutine_name
                        num_args = 1

                    else:
                        # term -> className '.' subroutineName '(' expressionList ')'
                        # tkn_txt is className
                        # (a SUBROUTINE call)
                        # .jack: PongGame.newInstance()
                        # .vm:   call PongGame.newInstance 0 // (no args)
                        call_name = tkn_txt.strip() + "." + subroutine_name

                     # e.g. 'new' or 'run'

                else:
                    # term -> subroutineName '(' expressionList ')'
                    # (a METHOD call)
                    # .jack: do moveBall()
                    # .vm    call PongGame.moveBall 1
                    self.vm_writer.write_push("POINTER", 0)
                    call_name = self.class_name + "." + identifier
                    num_args = 1

                self._eat_symbol("(")
                num_args += self._compile_expressison_list()
                self._eat_symbol(")")

                self.vm_writer.write_call(call_name, num_args)
                if not self.compiling_let:
                    self.vm_writer.write_pop("TEMP", 0)


            else:

                if self.symbol_table.recognises_symbol(identifier):
                    index = self.symbol_table.index_of(identifier)
                    kind = self.symbol_table.kind_of(identifier)
                    self.vm_writer.write_push(kind, index)


    @record_parent
    @reinstate_parent
    def _compile_expressison_list(self):
        """ Compiles a (possibly empty) comma-separated list of expressions """
        expression_list_node = ET.SubElement(self.current_node, 'expressionList')
        expression_list_node.text = "\n"
        if self.cur_tkn.text == ' ) ':
            expression_list_node.text = "\n"
            return 0

        expressions_counter = 0
        self.current_node = expression_list_node
        while True:

            self._compile_expression()
            expressions_counter += 1
            if self.cur_tkn.text != ' , ':
                break

            self._eat_symbol(",")

        return expressions_counter
    # Consuming tokens

    def _eat_symbol(self, expected_value=None):
        return self._validate_and_insert_current_token("symbol", expected_value).text.strip()

    def _eat_identifier(self, expected_value=None):

        return self._validate_and_insert_current_token("identifier", expected_value).text.strip()

    def _eat_string_constant(self, expected_value=None):
        return self._validate_and_insert_current_token("stringConstant", expected_value).text.strip()

    def _eat_integer_constant(self, expected_value=None):
        return self._validate_and_insert_current_token("integerConstant", expected_value).text.strip()

    def _eat_keyword(self, expected_value=None):
        return self._validate_and_insert_current_token("keyword", expected_value).text.strip()

    def _eat(self, expected_value=None, expected_pattern=None):
        subelement = self._validate_and_insert_current_token(expected_value=expected_value,
                                                             expected_pattern=expected_pattern)
        return subelement.text.strip()

    def _validate_and_insert_current_token(self, expected_type=None, expected_value=None, expected_pattern=None):
        tkn_type = self.cur_tkn.tag
        tkn_text = self.cur_tkn.text
        if expected_type is not None:
            assert tkn_type == expected_type, \
                "unexpected token type; type of current token '{}' is '{}', not '{}'".format(tkn_text, tkn_type, expected_type)
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
        return sub_element

def stringify_xml(elem):
    """ Return a pretty-printed XML string for the Element. """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    pretty_string = reparsed.toprettyxml(indent="    ")
    return "\n".join(list(filter(lambda x: True if len(x.strip()) > 0 else False, pretty_string.split("\n"))))