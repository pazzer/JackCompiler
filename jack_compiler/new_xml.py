__author__ = 'paulpatterson'

from lxml import etree

class Color():

    def __init__(self, red, green, blue):
        self.red = red
        self.blue = blue
        self.green = green

    @property
    def colors(self):
        return self.red, self.green, self.blue

if __name__ == "__main__":
    root = etree.Element("root")
    tree = etree.ElementTree()
    tree._setroot(root)


    root = tree.getroot()

    child = etree.SubElement(root, "child1")
    child.text = "hello"

    print((etree.tostring(root, pretty_print=True)).decode('utf-8'))

    c = Color(red=34, green=241, blue=100)
    print(c.colors)





