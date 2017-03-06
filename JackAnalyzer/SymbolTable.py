__author__ = 'paulpatterson'

## FIELD and STATIC variables have class-level scope - they can be accessed from any part of the class - and as such
## they belong in the class-level symbol table.
##
## The scope of local and argument variables is the subroutine in which they are defined, they therefore belong in the
## subroutine-level symbol table.
##
## Each time we start compiling a new class, we can start to compile a new class-level symbol table. Likewise, when
## we start to compile a new subroutine, we can discard the previous sub-routine level symbol table, and start afresh.

class SymbolTable():

    def __init__(self):
        self._class_symbols = {}
        self._subroutine_symbols = {}

    def start_subroutine(self):
        self._subroutine_symbols.clear()

    def define(self, name, type, kind):
        """Defines a new identifier of the given name, type, and kind and assigns it a running index.

        STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope."""
        pass

    def var_count(self, kind):
        """Returns the number of variables of the given kind already defined in the current scope.

        [kind] should be one of field, static, arg, or var"""
        pass

    def kind_of(self, name):
        """Returns the kind of the named identifier in the current scope. If the identifier is unknown in the current
        scope, returns None

        [name] should be one of static, field, arf, var or none
        """
        pass

    def type_of(self, name):
        """Returns the type of the named identifier in the current scope"""
        pass

    def index_of(self, name):
        """Returns the index assigned to the named identifier"""
        pass
