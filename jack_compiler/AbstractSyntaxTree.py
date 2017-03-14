__author__ = 'paulpatterson'

from lxml import etree
from functools import reduce

class AbstractSyntaxTree():

    def __init__(self, root_node=None):
        self._tree = None
        self._current_node = None

        if root_node is not None:
            self.current_node = root_node
            self._tree = etree.ElementTree(root_node)

    def _get_enclosing_node(self, tag):
        ancestor = self.current_node
        while ancestor.tag != tag:
            ancestor = ancestor.getparent()
        return ancestor

    @property
    def stmt(self):
        ancestor = self.current_node
        while ancestor.tag.find("Statement") == -1:
            ancestor = ancestor.getparent()
        return ancestor

    @property
    def class_name(self):
        class_node = self._tree.getroot()
        return class_node.find("./identifier").text.strip()

    @property
    def subroutine_name(self):
        subroutine_dec = self._get_enclosing_node("subroutineDec")
        return list(subroutine_dec)[2].text.strip()

    @property
    def num_subroutine_params(self):
        subroutineDec = self._get_enclosing_node("subroutineDec")
        explicit_params = len(subroutineDec.findall("parameterList/identifier"))
        return explicit_params if self.subroutine_kind != "method" else explicit_params + 1

    @property
    def num_subroutine_locals(self):
        subroutineBody = self._get_enclosing_node("subroutineBody")
        var_decs = [list(var_dec) for var_dec in subroutineBody.findall("varDec")]
        return int(sum(map(lambda x: 1 + ((x - 4) / 2), [len(list(var_dec)) for var_dec in var_decs])))

    @property
    def subroutine_kind(self):
        subroutine_dec = self._get_enclosing_node("subroutineDec")
        return list(subroutine_dec)[0].text.strip()

    def append(self, tag, text=None):
        if self._tree is None:
            new_node = etree.Element(tag)
            self._tree = etree.ElementTree(new_node)
        else:
            new_node = etree.SubElement(self.current_node, tag)

        if text is not None:
            new_node.text = text

        self.current_node = new_node

        return new_node

    def append_leaf(self, tag, text=None):
        new_node = etree.SubElement(self.current_node, tag)
        if text is not None:
            new_node.text = text
        return new_node

    def enclosing_stmt(self):
        pass

    @property
    def current_node(self):
        return self._current_node

    @current_node.setter
    def current_node(self, value):
        self._current_node = value

    def __str__(self):
        return etree.tostring(self._tree, pretty_print=True).decode("utf-8")




