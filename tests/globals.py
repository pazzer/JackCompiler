__author__ = 'paulpatterson'

from pathlib import Path

PROJ_10_DIR = "/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/nand2tetris/projects/10/"


XML_CLASS_WRAPPER = \
"""
<class>
  <keyword> class </keyword>
  <identifier> Test </identifier>
  <symbol> {{ </symbol>
  {}
  <symbol> }} </symbol>
</class>
"""

SNIPPET_CLASS_WRAPPER = \
"""
class Test {{
    {0}
}}
"""

ACTUAL_COMPARE = Path("/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/actual.txt")
EXPECTED_COMPARE = Path("/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/expected.txt")