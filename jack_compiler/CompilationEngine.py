__author__ = 'paulpatterson'

import re
from jack_compiler.SymbolTable import SymbolTable
from jack_compiler.AbstractSyntaxTree import AbstractSyntaxTree

OPERATORS = [" + ", " - ", " * ", " / ", " & ", " | ", " < ", " > ", " = "]
TYPE_PATTERN = r" int | char | boolean | [a-zA-Z_][a-zA-Z0-9_]* "


class CompilationEngine():

    def __init__(self, tokenizer=None, vm_writer=None):
        """ Creates a new compilation engine with the given input and output. The next routine called must be
        compile_class """
        self.tknzr = tokenizer
        self.vm_writer = vm_writer
        self.symbol_table = SymbolTable()
        self.ast = AbstractSyntaxTree()

    @property
    def cur_tkn(self):
        return self.tknzr.current_token

    def compile(self):
        self.tknzr.advance()
        self._compile_class()

    def _compile_class(self):
        """ Compiles a complete class

        class: 'class' className '{' classVarDec* subroutineDec* '}'
        """
        assert self.cur_tkn.text == " class ", "unexpected 'class' as first token - got '{}'".format(self.cur_tkn.text)

        _ = self.ast.append(tag="class")

        self._eat_keyword("class")
        self._eat_identifier()
        self._eat_symbol("{")

        while self.cur_tkn.text in [" static ", " field "]:
            self._compile_class_var_dec()

        while self.cur_tkn.text in [" constructor ", " function ", " method "]:
            self._compile_subroutine_dec()

        self._eat_symbol("}")

    def _compile_class_var_dec(self):
        """ Compiles a static variable declaration, or a field declaration """
        if self.cur_tkn.text not in [" static ", " field "]:
            return

        class_var_dec = self.ast.append("classVarDec")

        field_or_static = self._eat_keyword()
        var_type = self._eat(expected_pattern=TYPE_PATTERN)
        var_name = self._eat_identifier()
        self.symbol_table.define(var_name, var_type, field_or_static.upper())

        while self.cur_tkn.text == " , ":
            self._eat_symbol(",")
            var_name = self._eat_identifier()
            self.symbol_table.define(var_name, var_type, field_or_static.upper())

        self._eat_symbol(";")
        self.ast.current_node = class_var_dec.getparent()

    def _compile_subroutine_dec(self):
        """ Compiles a complete method, function, or constructor """
        if self.cur_tkn.text not in [" constructor ", " function ", " method "]:
            return False

        self.symbol_table.start_subroutine()
        subroutine_dec = self.ast.append(tag="subroutineDec")

        if self._eat_keyword() == "method":
            self.symbol_table.define("this", self.ast.class_name, "ARG")
        self._eat()
        self._eat_identifier()  # subroutine name

        self._eat_symbol("(")
        self._compile_parameter_list()
        self._eat_symbol(")")
        self._compile_subroutine_body()

        self.ast.current_node = subroutine_dec.getparent()

    def _compile_parameter_list(self):
        """ Compiles a (possibly empty) parameter list. Does not handle the enclosing '()' """
        parameter_list = self.ast.append(tag="parameterList")

        while self.cur_tkn.text != " ) ":

            var_type = self._eat(expected_pattern=TYPE_PATTERN)
            var_name = self._eat_identifier()
            self.symbol_table.define(var_name, var_type, "ARG")

            if self.cur_tkn.text == " , ":
                _ = self._eat_symbol(",")

        self.ast.current_node = parameter_list.getparent()

    def _compile_subroutine_body(self):
        """ Compiles a subroutine's body """
        subroutine_body = self.ast.append("subroutineBody")
        self.counters = {"if": 0, "while": 0}

        self._eat_symbol("{")

        while self.cur_tkn.text == " var ":
            self._compile_var_dec()

        ## Write the signature
        func_name = "{}.{}".format(self.ast.class_name, self.ast.subroutine_name)
        self.vm_writer.write_function(func_name, self.ast.num_subroutine_locals)

        if self.ast.subroutine_is_constructor:
            self.vm_writer.write_push("CONST", self.symbol_table.var_count("FIELD"))
            self.vm_writer.write_call("Memory.alloc", 1)
            self.vm_writer.write_pop("POINTER", 0)
        elif self.ast.subroutine_is_method:
            self.vm_writer.write_push("ARG", 0)
            self.vm_writer.write_pop("POINTER", 0)

        self._compile_statements()
        self._eat_symbol("}")

        self.ast.current_node = subroutine_body.getparent()

    def _compile_var_dec(self):
        """ Compiles a 'var' declaration

        a 'varDec' element is only added if their is at least one variable declaration """
        if self.cur_tkn.text != " var ":
            return

        var_dec = self.ast.append(tag="varDec")

        self._eat_keyword("var")
        var_type = self._eat(expected_pattern=TYPE_PATTERN)

        while True:

            assert self.cur_tkn.tag == "identifier", \
                "expected keyword or identifier, got ' {} '".format(self.cur_tkn.text)
            var_name = self._eat_identifier()
            self.symbol_table.define(var_name, var_type, "VAR")

            previous_token = self.cur_tkn
            self._eat_symbol([";", ","])

            if previous_token.text == " ; ":
                break

        self.ast.current_node = var_dec.getparent()

    def _compile_statements(self):
        """ Compiles a sequence of statements. Does not handle the enclosing '{}'

        Hint: Uses a loop to handle zero or more statement instances, according to the left-most token.
        If the left-most token is 'if', 'while'..., ...it invokes 'compile_if', 'compile_while', ....

        Note: There is no compile_statement method
        """
        stmts = self.ast.append(tag="statements")

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
            else:
                self._compile_return()

        self.ast.current_node = stmts.getparent()

    def _compile_let(self):
        """ Compiles a 'let' statement """
        let_stmt = self.ast.append(tag="letStatement")

        self._eat_keyword("let")
        var_name = self._eat_identifier()
        array_assignment = False

        if self.cur_tkn.text == ' [ ':
            symbol = self.symbol_table.info_for_symbol(var_name)
            array_assignment = True
            self._eat_symbol("[")
            self._compile_expression()
            self.vm_writer.write_push(symbol.kind, symbol.index)
            self.vm_writer.write_arithmetic("ADD")
            self._eat_symbol("]")

        self._eat_symbol("=")
        self._compile_expression()

        if array_assignment:
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            symbol = self.symbol_table.info_for_symbol(var_name)
            if symbol is not None:
                self.vm_writer.write_pop(symbol.kind, symbol.index)

        self._eat_symbol(";")

        self.ast.current_node = let_stmt.getparent()

    def _compile_if(self):
        """ Compiles an 'if' statement, possibly with a trailing 'else' clause """
        if_stmt = self.ast.append(tag="ifStatement")

        label_suffix = self.counters["if"]
        self.counters["if"] = label_suffix + 1

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

        self.ast.current_node = if_stmt.getparent()

    def _compile_while(self):
        """ Compiles a 'while' statement """
        while_stmt = self.ast.append(tag="whileStatement")

        label_suffix = self.counters["while"]
        self.counters["while"] = label_suffix + 1

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

        self.ast.current_node = while_stmt.getparent()

    def _compile_do(self):
        """ Compiles a 'do' statement """

        do_stmt = self.ast.append("doStatement")
        self._eat_keyword("do")
        self._compile_term()  # term will 'expand' to 'subroutineCall'
        self._eat_symbol(";")

        self.ast.current_node = do_stmt.getparent()

    def _compile_return(self):
        """ Compiles a 'return' statement """

        return_stmt = self.ast.append("returnStatement")
        self._eat_keyword("return")

        if self.cur_tkn.text != " ; ":
            self._compile_expression()
        else:
            self.vm_writer.write_push("CONST", 0)

        self.vm_writer.write_return()
        self._eat_symbol(";")

        self.ast.current_node = return_stmt.getparent()

    def _compile_expression(self):
        """ Compiles an expression """

        expression = self.ast.append(tag="expression")
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
            elif command == "&":
                self.vm_writer.write_arithmetic("AND")
            elif command == "*":
                self.vm_writer.write_call("Math.multiply", 2)
            else:
                assert command == "/", "unexpected command '{}', expected '/'".format(command)
                self.vm_writer.write_call("Math.divide", 2)

        self.ast.current_node = expression.getparent()

    def _compile_term(self):
        """ Compiles a term

        If the current token is an identifier, the routines must distinguish between a variable, an array entry, or a
        subroutine call. A single lookahead token (which may be one of '[', '(', or '.') suffices to distinguish
        between the possibilities. Any other token is not part of this term and should not be advanced over. """
        term = self.ast.append("term") if self.ast.current_node.tag != "doStatement" else None

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
            else:
                assert tkn_txt == " this ", "expected ' this ', got {}".format(tkn_txt)
                self.vm_writer.write_push("POINTER", 0)

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
                self.calling_method = False
                if self.cur_tkn.text == " . ":
                    self._eat_symbol(".")
                    subroutine_name = self._eat_identifier().strip()

                    if self.symbol_table.recognises_symbol(tkn_txt.strip()):
                        # term -> varName '.' subroutineName '(' expressionList ')'  // a method call
                        # tkn_text is a varName
                        # .jack: do game.run()
                        # .vm:   function PongGame.run 1 // 1 arg (self)
                        symbol = self.symbol_table.info_for_symbol(tkn_txt.strip())
                        self.vm_writer.write_push(symbol.kind, symbol.index)
                        call_name = symbol.type + "." + subroutine_name
                        self.calling_method = True

                    else:
                        # term -> className '.' subroutineName '(' expressionList ')'  // a subroutine call
                        # tkn_txt is className
                        # .jack: PongGame.newInstance()
                        # .vm:   call PongGame.newInstance 0 // (no args)
                        call_name = tkn_txt.strip() + "." + subroutine_name

                else:
                    # term -> subroutineName '(' expressionList ')'  // a method call
                    # .jack: do moveBall()
                    # .vm:   call PongGame.moveBall 1
                    self.vm_writer.write_push("POINTER", 0)
                    call_name = self.ast.class_name + "." + identifier
                    self.calling_method = True

                self._eat_symbol("(")
                self._compile_expressison_list()
                self._eat_symbol(")")

                num_args = len(self.ast.current_node.findall("expressionList/expression"))
                num_args += 1 if self.calling_method else 0
                self.vm_writer.write_call(call_name, num_args)

                if self.ast.stmt.tag.find("let") == -1:
                    self.vm_writer.write_pop("TEMP", 0)

            else:
                symbol_info = self.symbol_table.info_for_symbol(identifier)
                if symbol_info is not None:
                    self.vm_writer.write_push(symbol_info.kind, symbol_info.index)

        if term is not None:
            self.ast.current_node = term.getparent()

    def _compile_expressison_list(self):
        """ Compiles a (possibly empty) comma-separated list of expressions """
        expression_list = self.ast.append("expressionList")

        if self.cur_tkn.text != ' ) ':
            while True:
                self._compile_expression()
                if self.cur_tkn.text != ' , ':
                    break
                self._eat_symbol(",")

        self.ast.current_node = expression_list.getparent()

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

        subelement = self.ast.append_leaf(tag=self.cur_tkn.tag, text=self.cur_tkn.text)

        self.tknzr.advance()
        return subelement