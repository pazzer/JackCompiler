__author__ = 'paulpatterson'

import xml.etree.ElementTree as ET
import unittest
from pathlib import Path

from JackAnalyzer.JackAnalyzer import JackAnalyzer
from JackAnalyzer.CompilationEngine import stringify_xml
from tests.globals import XML_CLASS_WRAPPER, SNIPPET_CLASS_WRAPPER

def moderate_do():
    snippet = \
"""
   method void draw() {
      do Screen.drawRectangle(x, y, x + size, y + size);
      return;
   }
"""
    analyzed = \
"""
  <subroutineDec>
    <keyword> method </keyword>
    <keyword> void </keyword>
    <identifier> draw </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <doStatement>
          <keyword> do </keyword>
          <identifier> Screen </identifier>
          <symbol> . </symbol>
          <identifier> drawRectangle </identifier>
          <symbol> ( </symbol>
          <expressionList>
            <expression>
              <term>
                <identifier> x </identifier>
              </term>
            </expression>
            <symbol> , </symbol>
            <expression>
              <term>
                <identifier> y </identifier>
              </term>
            </expression>
            <symbol> , </symbol>
            <expression>
              <term>
                <identifier> x </identifier>
              </term>
              <symbol> + </symbol>
              <term>
                <identifier> size </identifier>
              </term>
            </expression>
            <symbol> , </symbol>
            <expression>
              <term>
                <identifier> y </identifier>
              </term>
              <symbol> + </symbol>
              <term>
                <identifier> size </identifier>
              </term>
            </expression>
          </expressionList>
          <symbol> ) </symbol>
          <symbol> ; </symbol>
        </doStatement>
        <returnStatement>
          <keyword> return </keyword>
          <symbol> ; </symbol>
        </returnStatement>
      </statements>
      <symbol> } </symbol>
    </subroutineBody>
  </subroutineDec>
"""

    wrapped_snippet = SNIPPET_CLASS_WRAPPER.format(snippet)
    wrapped_xml = XML_CLASS_WRAPPER.format(analyzed)

    return wrapped_snippet, ET.fromstring(wrapped_xml)

def simple_do():
    snippet = \
"""
   method void dispose() {
      do square.dispose();
      return;
   }"""

    analyzed = \
"""
  <subroutineDec>
    <keyword> method </keyword>
    <keyword> void </keyword>
    <identifier> dispose </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <doStatement>
          <keyword> do </keyword>
          <identifier> square </identifier>
          <symbol> . </symbol>
          <identifier> dispose </identifier>
          <symbol> ( </symbol>
          <expressionList>
</expressionList>
          <symbol> ) </symbol>
          <symbol> ; </symbol>
        </doStatement>
        <returnStatement>
          <keyword> return </keyword>
          <symbol> ; </symbol>
        </returnStatement>
      </statements>
      <symbol> } </symbol>
    </subroutineBody>
  </subroutineDec>
  """

    wrapped_snippet = SNIPPET_CLASS_WRAPPER.format(snippet)
    wrapped_xml = XML_CLASS_WRAPPER.format(analyzed)

    return wrapped_snippet, ET.fromstring(wrapped_xml)

def complex_do():
    snippet = \
"""
   method void draw() {
      do Screen.drawRectangle(x, (y + size) - 1);
      return;
   }
"""
    analyzed = \
"""
  <subroutineDec>
    <keyword> method </keyword>
    <keyword> void </keyword>
    <identifier> draw </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <doStatement>
          <keyword> do </keyword>
          <identifier> Screen </identifier>
          <symbol> . </symbol>
          <identifier> drawRectangle </identifier>
          <symbol> ( </symbol>
          <expressionList>
                <expression>
                  <term>
                    <identifier> x </identifier>
                  </term>
                </expression>
                <symbol> , </symbol>
                <expression>
                  <term>
                    <symbol> ( </symbol>
                    <expression>
                      <term>
                        <identifier> y </identifier>
                      </term>
                      <symbol> + </symbol>
                      <term>
                        <identifier> size </identifier>
                      </term>
                    </expression>
                    <symbol> ) </symbol>
                  </term>
                  <symbol> - </symbol>
                  <term>
                    <integerConstant> 1 </integerConstant>
                  </term>
                </expression>
          </expressionList>
          <symbol> ) </symbol>
          <symbol> ; </symbol>
        </doStatement>
        <returnStatement>
          <keyword> return </keyword>
          <symbol> ; </symbol>
        </returnStatement>
      </statements>
      <symbol> } </symbol>
    </subroutineBody>
  </subroutineDec>
"""

    wrapped_snippet = SNIPPET_CLASS_WRAPPER.format(snippet)
    wrapped_xml = XML_CLASS_WRAPPER.format(analyzed)

    return wrapped_snippet, ET.fromstring(wrapped_xml)

def severe_do():
    snippet = \
"""
   method void draw() {
      do Screen.drawRectangle(x, (y + size) - 1, x + size, y + size);
      return;
   }
"""

    analyzed = \
"""
  <subroutineDec>
    <keyword> method </keyword>
    <keyword> void </keyword>
    <identifier> draw </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <doStatement>
          <keyword> do </keyword>
          <identifier> Screen </identifier>
          <symbol> . </symbol>
          <identifier> drawRectangle </identifier>
          <symbol> ( </symbol>
          <expressionList>
                <expression>
                  <term>
                    <identifier> x </identifier>
                  </term>
                </expression>
                <symbol> , </symbol>
                <expression>
                  <term>
                    <symbol> ( </symbol>
                    <expression>
                      <term>
                        <identifier> y </identifier>
                      </term>
                      <symbol> + </symbol>
                      <term>
                        <identifier> size </identifier>
                      </term>
                    </expression>
                    <symbol> ) </symbol>
                  </term>
                  <symbol> - </symbol>
                  <term>
                    <integerConstant> 1 </integerConstant>
                  </term>
                </expression>
                <symbol> , </symbol>
                <expression>
                  <term>
                    <identifier> x </identifier>
                  </term>
                  <symbol> + </symbol>
                  <term>
                    <identifier> size </identifier>
                  </term>
                </expression>
                <symbol> , </symbol>
                <expression>
                  <term>
                    <identifier> y </identifier>
                  </term>
                  <symbol> + </symbol>
                  <term>
                    <identifier> size </identifier>
                  </term>
                </expression>
          </expressionList>
          <symbol> ) </symbol>
          <symbol> ; </symbol>
        </doStatement>
        <returnStatement>
          <keyword> return </keyword>
          <symbol> ; </symbol>
        </returnStatement>
      </statements>
      <symbol> } </symbol>
    </subroutineBody>
  </subroutineDec>
"""

    wrapped_snippet = SNIPPET_CLASS_WRAPPER.format(snippet)
    wrapped_xml = XML_CLASS_WRAPPER.format(analyzed)

    return wrapped_snippet, ET.fromstring(wrapped_xml)



ACTUAL_COMPARE = Path("/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/actual.txt")
EXPECTED_COMPARE = Path("/Users/paulpatterson/Documents/MacProgramming/Nand2Tetris/expected.txt")

class CustomAnalyzerTests(unittest.TestCase):

    def _prepare_test(self, snippet, expected_xml):
        analyzer = JackAnalyzer.analyzer_for_snippet(snippet)
        actual_xml = analyzer.analyze(return_results=True)

        actual_string = stringify_xml(actual_xml.getroot())
        expected_string = stringify_xml(expected_xml)

        with open(ACTUAL_COMPARE.as_posix(), 'w') as compOne:
            with open(EXPECTED_COMPARE.as_posix(), 'w') as compareTwo:
                compOne.write(actual_string)
                compareTwo.write(expected_string)

        actual_string = stringify_xml(actual_xml.getroot())
        expected_string = stringify_xml(expected_xml)

        return actual_string, expected_string

    def test_simple_do(self):
        actual_string, expected_string = self._prepare_test(*simple_do())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_moderate_do(self):
        actual_string, expected_string = self._prepare_test(*moderate_do())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_complex_do(self):
        actual_string, expected_string = self._prepare_test(*complex_do())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_severe_do(self):
        actual_string, expected_string = self._prepare_test(*severe_do())
        self.assertMultiLineEqual(actual_string, expected_string)