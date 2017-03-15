__author__ = 'paulpatterson'

from lxml import etree


class AbstractSyntaxTree():

    def __init__(self, root_node=None):
        """ Creates a new AbstractSyntaxTree instance. If root_node != none, it becomes the root node of the tree. """
        self._tree = None
        self._current_node = None

        if root_node is not None:
            self.current_node = root_node
            self._tree = etree.ElementTree(root_node)

    @property
    def stmt(self):
        """ Returns the nearest statement node ancestor of current_node, otherwise returns None. """
        ancestor = self.current_node
        while ancestor.tag.find("Statement") == -1:
            ancestor = ancestor.getparent()
        return ancestor

    @property
    def class_name(self):
        """ Returns the class name of the enclosing class node. """
        class_node = self._tree.getroot()
        return class_node.find("./identifier").text.strip()

    @property
    def subroutine_name(self):
        """ Returns the name of the subroutine that encloses current_node. """
        subroutine_dec = self._get_enclosing_node("subroutineDec")
        return list(subroutine_dec)[2].text.strip()

    @property
    def num_subroutine_params(self):
        """ Returns the number of parameters declared by the subroutine enclosing current_node. """
        subroutineDec = self._get_enclosing_node("subroutineDec")
        explicit_params = len(subroutineDec.findall("parameterList/identifier"))
        return explicit_params if self.subroutine_kind != "method" else explicit_params + 1

    @property
    def num_subroutine_locals(self):
        """ Returns the number of local variables declared by the subroutine enclosing current_node. """
        subroutineBody = self._get_enclosing_node("subroutineBody")
        var_decs = [list(var_dec) for var_dec in subroutineBody.findall("varDec")]
        return int(sum(map(lambda x: 1 + ((x - 4) / 2), [len(list(var_dec)) for var_dec in var_decs])))

    @property
    def subroutine_kind(self):
        """ Returns the kind (method, constructor, function) of the subroutine enclosing current_node. """
        subroutine_dec = self._get_enclosing_node("subroutineDec")
        return list(subroutine_dec)[0].text.strip()

    @property
    def subroutine_is_method(self):
        """ Returns True if the subroutine enclosing current_node is a method, otherwise returns False. """
        subroutine_dec = self._get_enclosing_node("subroutineDec")
        return list(subroutine_dec)[0].text.strip() == "method"

    @property
    def subroutine_is_constructor(self):
        """ Returns True if the subroutine enclosing current_node is a constructor, otherwise returns False. """
        subroutine_dec = self._get_enclosing_node("subroutineDec")
        return list(subroutine_dec)[0].text.strip() == "constructor"

    @property
    def current_node(self):
        """ Returns the current_node. """
        return self._current_node

    @current_node.setter
    def current_node(self, value):
        """ Sets the current node (value must be an Element instance). """
        self._current_node = value

    def append(self, tag, text=None):
        """ Creates a node and adds it to the children of current_node. Finally, this new node becomes current_node. """
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
        """ Creates a node and adds it to the children of current node.

        Unlike ``append`` this method does not make the newly created node the current_node."""
        new_node = etree.SubElement(self.current_node, tag)
        if text is not None:
            new_node.text = text
        return new_node

    def write(self, file_path):
        """ Writes the contents of """
        assert file_path.exists(), "no such file '{}'".format(file_path)
        with open(file_path.as_posix(), 'w') as outfile:
            outfile.write(str(self))

    def _get_enclosing_node(self, tag):
        """ Searches current_node's ancestors for a node whose tag matches the specified tag. """
        ancestor = self.current_node
        while ancestor.tag != tag:
            ancestor = ancestor.getparent()
        return ancestor

    def __str__(self):
        """ Returns a formatted xml string representing the contents of the tree. """
        return etree.tostring(self._tree, pretty_print=True).decode("utf-8")


def stringify_xml(elem):
    """ Return a pretty-printed XML string for the Element. """
    return etree.tostring(elem, pretty_print=True).decode("utf-8")

