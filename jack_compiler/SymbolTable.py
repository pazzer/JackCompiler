__author__ = 'paulpatterson'

## FIELD and STATIC variables have class-level scope - they can be accessed from any part of the class - and as such
## they belong in the class-level symbol table.
##
## The scope of local and argument variables is the subroutine in which they are defined, they therefore belong in the
## subroutine-level symbol table.
##
## Each time we start compiling a new class, we can start to compile a new class-level symbol table. Likewise, when
## we start to compile a new subroutine, we can discard the previous sub-routine level symbol table, and start afresh.

from collections import namedtuple
from collections import OrderedDict
Symbol = namedtuple("Symbol", "type kind index")

class SymbolTable():

    def __init__(self):
        self._class_symbols = OrderedDict()
        self._subroutine_symbols = OrderedDict()

    def subroutine_is_method(self):
        return "this" in self._subroutine_symbols.keys()

    def start_subroutine(self):
        self._subroutine_symbols.clear()

    def output_subroutine_symbols(self):
        for k, v in self._subroutine_symbols.items():
            print("{}: {}, {}, {}".format(k, v.type, v.kind, v.index))

    def output_class_symbols(self):
        for k, v in self._class_symbols.items():
            print("{}:{}, {}, {}".format(k, v.type, v.kind, v.index))

    def output_all_symbols(self):
        print("class-level symbols")
        self.output_class_symbols()
        print("subroutine symbols")
        self.output_subroutine_symbols()


    def define(self, name, var_type, kind):
        """Defines a new identifier of the given name, type, and kind and assigns it a running index.

        STATIC and FIELD identifiers have a class scope, while ARG and VAR identifiers have a subroutine scope."""
        symbol_table = self._class_symbols if kind in ["STATIC", "FIELD"] else self._subroutine_symbols
        symbol_table[name] = Symbol(var_type, kind, self.var_count(kind))

    def var_count(self, kind):
        """Returns the number of variables of the given kind already defined in the current scope.

        [kind] should be one of field, static, arg, or var"""
        symbol_table = self._class_symbols if kind in ["STATIC", "FIELD"] else self._subroutine_symbols
        return len(list(filter(lambda x: x.kind == kind, symbol_table.values())))


    def kind_of(self, name):
        """Returns the kind of the named identifier in the current scope. If the identifier is unknown in the current
        scope, returns None

        [name] should be one of static, field, arg, var or none
        """
        if name in self._subroutine_symbols.keys():
            return self._subroutine_symbols[name].kind
        elif name in self._class_symbols.keys():
            return self._class_symbols[name].kind
        else:
            return None

    def type_of(self, name):
        """Returns the type of the named identifier in the current scope"""
        if name in self._subroutine_symbols.keys():
            return self._subroutine_symbols[name].type
        elif name in self._class_symbols.keys():
            return self._class_symbols[name].type
        else:
            return None

    def index_of(self, name):
        """Returns the index assigned to the named identifier"""
        if name in self._subroutine_symbols.keys():
            return self._subroutine_symbols[name].index
        elif name in self._class_symbols.keys():
            return self._class_symbols[name].index
        else:
            return None

    def info_for_symbol(self, name):
        if self.recognises_symbol(name):
            return Symbol(self.type_of(name), self.kind_of(name), self.index_of(name))

    def recognises_symbol(self, name):
        return name in self._class_symbols.keys() or name in self._subroutine_symbols.keys()
