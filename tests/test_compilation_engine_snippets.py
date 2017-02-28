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


def non_void_return():
    snippet = \
"""
   constructor Square new(int Ax, int Ay, int Asize) {
      do draw();
      return this;
   }
"""
    analyzed = \
"""
 <subroutineDec>
    <keyword> constructor </keyword>
    <identifier> Square </identifier>
    <identifier> new </identifier>
    <symbol> ( </symbol>
    <parameterList>
      <keyword> int </keyword>
      <identifier> Ax </identifier>
      <symbol> , </symbol>
      <keyword> int </keyword>
      <identifier> Ay </identifier>
      <symbol> , </symbol>
      <keyword> int </keyword>
      <identifier> Asize </identifier>
    </parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <doStatement>
          <keyword> do </keyword>
          <identifier> draw </identifier>
          <symbol> ( </symbol>
          <expressionList>
</expressionList>
          <symbol> ) </symbol>
          <symbol> ; </symbol>
        </doStatement>
        <returnStatement>
          <keyword> return </keyword>
          <expression>
            <term>
              <keyword> this </keyword>
            </term>
          </expression>
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


def class_level_vars():
    snippet = \
"""
   field Square square, counter;
   field int direction;

"""

    analyzed = \
"""
 <classVarDec>
    <keyword> field </keyword>
    <identifier> Square </identifier>
    <identifier> square </identifier>
    <symbol> , </symbol>
    <identifier> counter </identifier>
    <symbol> ; </symbol>
  </classVarDec>
  <classVarDec>
    <keyword> field </keyword>
    <keyword> int </keyword>
    <identifier> direction </identifier>
    <symbol> ; </symbol>
  </classVarDec>
"""

    wrapped_snippet = SNIPPET_CLASS_WRAPPER.format(snippet)
    wrapped_xml = XML_CLASS_WRAPPER.format(analyzed)

    return wrapped_snippet, ET.fromstring(wrapped_xml)


def multiple_funcs():
    snippet = \
"""
   constructor SquareGame new() {
      return this;
   }

   method void dispose() {
      do square.dispose();
      do Memory.deAlloc(this);
      return;
   }
"""
    analyzed = \
"""
  <subroutineDec>
    <keyword> constructor </keyword>
    <identifier> SquareGame </identifier>
    <identifier> new </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <returnStatement>
          <keyword> return </keyword>
          <expression>
            <term>
              <keyword> this </keyword>
            </term>
          </expression>
          <symbol> ; </symbol>
        </returnStatement>
      </statements>
      <symbol> } </symbol>
    </subroutineBody>
  </subroutineDec>
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
        <doStatement>
          <keyword> do </keyword>
          <identifier> Memory </identifier>
          <symbol> . </symbol>
          <identifier> deAlloc </identifier>
          <symbol> ( </symbol>
          <expressionList>
            <expression>
              <term>
                <keyword> this </keyword>
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


def let():
    snippet = \
"""
constructor SquareGame new() {
      let square = Square.new(0, 0, 30);
      let direction = 0;
      return this;
   }
"""

    analyzed = \
"""
  <subroutineDec>
    <keyword> constructor </keyword>
    <identifier> SquareGame </identifier>
    <identifier> new </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <letStatement>
          <keyword> let </keyword>
          <identifier> square </identifier>
          <symbol> = </symbol>
          <expression>
            <term>
              <identifier> Square </identifier>
              <symbol> . </symbol>
              <identifier> new </identifier>
              <symbol> ( </symbol>
              <expressionList>
                <expression>
                  <term>
                    <integerConstant> 0 </integerConstant>
                  </term>
                </expression>
                <symbol> , </symbol>
                <expression>
                  <term>
                    <integerConstant> 0 </integerConstant>
                  </term>
                </expression>
                <symbol> , </symbol>
                <expression>
                  <term>
                    <integerConstant> 30 </integerConstant>
                  </term>
                </expression>
              </expressionList>
              <symbol> ) </symbol>
            </term>
          </expression>
          <symbol> ; </symbol>
        </letStatement>
        <letStatement>
          <keyword> let </keyword>
          <identifier> direction </identifier>
          <symbol> = </symbol>
          <expression>
            <term>
              <integerConstant> 0 </integerConstant>
            </term>
          </expression>
          <symbol> ; </symbol>
        </letStatement>
        <returnStatement>
          <keyword> return </keyword>
          <expression>
            <term>
              <keyword> this </keyword>
            </term>
          </expression>
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


def if_do():
    snippet = \
"""
    method void moveSquare() {
        if (direction = 1) { do square.moveUp(); }
        if (direction = 2) { do square.moveDown(); }
        if (direction = 3) { do square.moveLeft(); }
        if (direction = 4) { do square.moveRight(); }
        do Sys.wait(5);
        return;
    }
"""
    analyzed = \
"""
  <subroutineDec>
    <keyword> method </keyword>
    <keyword> void </keyword>
    <identifier> moveSquare </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <statements>
        <ifStatement>
          <keyword> if </keyword>
          <symbol> ( </symbol>
          <expression>
            <term>
              <identifier> direction </identifier>
            </term>
            <symbol> = </symbol>
            <term>
              <integerConstant> 1 </integerConstant>
            </term>
          </expression>
          <symbol> ) </symbol>
          <symbol> { </symbol>
          <statements>
            <doStatement>
              <keyword> do </keyword>
              <identifier> square </identifier>
              <symbol> . </symbol>
              <identifier> moveUp </identifier>
              <symbol> ( </symbol>
              <expressionList>
</expressionList>
              <symbol> ) </symbol>
              <symbol> ; </symbol>
            </doStatement>
          </statements>
          <symbol> } </symbol>
        </ifStatement>
        <ifStatement>
          <keyword> if </keyword>
          <symbol> ( </symbol>
          <expression>
            <term>
              <identifier> direction </identifier>
            </term>
            <symbol> = </symbol>
            <term>
              <integerConstant> 2 </integerConstant>
            </term>
          </expression>
          <symbol> ) </symbol>
          <symbol> { </symbol>
          <statements>
            <doStatement>
              <keyword> do </keyword>
              <identifier> square </identifier>
              <symbol> . </symbol>
              <identifier> moveDown </identifier>
              <symbol> ( </symbol>
              <expressionList>
</expressionList>
              <symbol> ) </symbol>
              <symbol> ; </symbol>
            </doStatement>
          </statements>
          <symbol> } </symbol>
        </ifStatement>
        <ifStatement>
          <keyword> if </keyword>
          <symbol> ( </symbol>
          <expression>
            <term>
              <identifier> direction </identifier>
            </term>
            <symbol> = </symbol>
            <term>
              <integerConstant> 3 </integerConstant>
            </term>
          </expression>
          <symbol> ) </symbol>
          <symbol> { </symbol>
          <statements>
            <doStatement>
              <keyword> do </keyword>
              <identifier> square </identifier>
              <symbol> . </symbol>
              <identifier> moveLeft </identifier>
              <symbol> ( </symbol>
              <expressionList>
</expressionList>
              <symbol> ) </symbol>
              <symbol> ; </symbol>
            </doStatement>
          </statements>
          <symbol> } </symbol>
        </ifStatement>
        <ifStatement>
          <keyword> if </keyword>
          <symbol> ( </symbol>
          <expression>
            <term>
              <identifier> direction </identifier>
            </term>
            <symbol> = </symbol>
            <term>
              <integerConstant> 4 </integerConstant>
            </term>
          </expression>
          <symbol> ) </symbol>
          <symbol> { </symbol>
          <statements>
            <doStatement>
              <keyword> do </keyword>
              <identifier> square </identifier>
              <symbol> . </symbol>
              <identifier> moveRight </identifier>
              <symbol> ( </symbol>
              <expressionList>
</expressionList>
              <symbol> ) </symbol>
              <symbol> ; </symbol>
            </doStatement>
          </statements>
          <symbol> } </symbol>
        </ifStatement>
        <doStatement>
          <keyword> do </keyword>
          <identifier> Sys </identifier>
          <symbol> . </symbol>
          <identifier> wait </identifier>
          <symbol> ( </symbol>
          <expressionList>
            <expression>
              <term>
                <integerConstant> 5 </integerConstant>
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


def test_while():
    snippet = \
"""
   method void run() {
      var char key;
      var boolean exit;
      let exit = false;

      while (~exit) {
         while (key = 0) {
            let key = Keyboard.keyPressed();
            do moveSquare();
         }
         if (key = 81)  { let exit = true; }
         if (key = 90)  { do square.decSize(); }
         if (key = 88)  { do square.incSize(); }
         if (key = 131) { let direction = 1; }
         if (key = 133) { let direction = 2; }
         if (key = 130) { let direction = 3; }
         if (key = 132) { let direction = 4; }

         while (~(key = 0)) {
            let key = Keyboard.keyPressed();
            do moveSquare();
         }
     }
     return;
   }
"""

    analyzed = \
"""
  <subroutineDec>
    <keyword> method </keyword>
    <keyword> void </keyword>
    <identifier> run </identifier>
    <symbol> ( </symbol>
    <parameterList>
</parameterList>
    <symbol> ) </symbol>
    <subroutineBody>
      <symbol> { </symbol>
      <varDec>
        <keyword> var </keyword>
        <keyword> char </keyword>
        <identifier> key </identifier>
        <symbol> ; </symbol>
      </varDec>
      <varDec>
        <keyword> var </keyword>
        <keyword> boolean </keyword>
        <identifier> exit </identifier>
        <symbol> ; </symbol>
      </varDec>
      <statements>
        <letStatement>
          <keyword> let </keyword>
          <identifier> exit </identifier>
          <symbol> = </symbol>
          <expression>
            <term>
              <keyword> false </keyword>
            </term>
          </expression>
          <symbol> ; </symbol>
        </letStatement>
        <whileStatement>
          <keyword> while </keyword>
          <symbol> ( </symbol>
          <expression>
            <term>
              <symbol> ~ </symbol>
              <term>
                <identifier> exit </identifier>
              </term>
            </term>
          </expression>
          <symbol> ) </symbol>
          <symbol> { </symbol>
          <statements>
            <whileStatement>
              <keyword> while </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 0 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <letStatement>
                  <keyword> let </keyword>
                  <identifier> key </identifier>
                  <symbol> = </symbol>
                  <expression>
                    <term>
                      <identifier> Keyboard </identifier>
                      <symbol> . </symbol>
                      <identifier> keyPressed </identifier>
                      <symbol> ( </symbol>
                      <expressionList>
</expressionList>
                      <symbol> ) </symbol>
                    </term>
                  </expression>
                  <symbol> ; </symbol>
                </letStatement>
                <doStatement>
                  <keyword> do </keyword>
                  <identifier> moveSquare </identifier>
                  <symbol> ( </symbol>
                  <expressionList>
</expressionList>
                  <symbol> ) </symbol>
                  <symbol> ; </symbol>
                </doStatement>
              </statements>
              <symbol> } </symbol>
            </whileStatement>
            <ifStatement>
              <keyword> if </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 81 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <letStatement>
                  <keyword> let </keyword>
                  <identifier> exit </identifier>
                  <symbol> = </symbol>
                  <expression>
                    <term>
                      <keyword> true </keyword>
                    </term>
                  </expression>
                  <symbol> ; </symbol>
                </letStatement>
              </statements>
              <symbol> } </symbol>
            </ifStatement>
            <ifStatement>
              <keyword> if </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 90 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <doStatement>
                  <keyword> do </keyword>
                  <identifier> square </identifier>
                  <symbol> . </symbol>
                  <identifier> decSize </identifier>
                  <symbol> ( </symbol>
                  <expressionList>
</expressionList>
                  <symbol> ) </symbol>
                  <symbol> ; </symbol>
                </doStatement>
              </statements>
              <symbol> } </symbol>
            </ifStatement>
            <ifStatement>
              <keyword> if </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 88 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <doStatement>
                  <keyword> do </keyword>
                  <identifier> square </identifier>
                  <symbol> . </symbol>
                  <identifier> incSize </identifier>
                  <symbol> ( </symbol>
                  <expressionList>
</expressionList>
                  <symbol> ) </symbol>
                  <symbol> ; </symbol>
                </doStatement>
              </statements>
              <symbol> } </symbol>
            </ifStatement>
            <ifStatement>
              <keyword> if </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 131 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <letStatement>
                  <keyword> let </keyword>
                  <identifier> direction </identifier>
                  <symbol> = </symbol>
                  <expression>
                    <term>
                      <integerConstant> 1 </integerConstant>
                    </term>
                  </expression>
                  <symbol> ; </symbol>
                </letStatement>
              </statements>
              <symbol> } </symbol>
            </ifStatement>
            <ifStatement>
              <keyword> if </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 133 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <letStatement>
                  <keyword> let </keyword>
                  <identifier> direction </identifier>
                  <symbol> = </symbol>
                  <expression>
                    <term>
                      <integerConstant> 2 </integerConstant>
                    </term>
                  </expression>
                  <symbol> ; </symbol>
                </letStatement>
              </statements>
              <symbol> } </symbol>
            </ifStatement>
            <ifStatement>
              <keyword> if </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 130 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <letStatement>
                  <keyword> let </keyword>
                  <identifier> direction </identifier>
                  <symbol> = </symbol>
                  <expression>
                    <term>
                      <integerConstant> 3 </integerConstant>
                    </term>
                  </expression>
                  <symbol> ; </symbol>
                </letStatement>
              </statements>
              <symbol> } </symbol>
            </ifStatement>
            <ifStatement>
              <keyword> if </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <identifier> key </identifier>
                </term>
                <symbol> = </symbol>
                <term>
                  <integerConstant> 132 </integerConstant>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <letStatement>
                  <keyword> let </keyword>
                  <identifier> direction </identifier>
                  <symbol> = </symbol>
                  <expression>
                    <term>
                      <integerConstant> 4 </integerConstant>
                    </term>
                  </expression>
                  <symbol> ; </symbol>
                </letStatement>
              </statements>
              <symbol> } </symbol>
            </ifStatement>
            <whileStatement>
              <keyword> while </keyword>
              <symbol> ( </symbol>
              <expression>
                <term>
                  <symbol> ~ </symbol>
                  <term>
                    <symbol> ( </symbol>
                    <expression>
                      <term>
                        <identifier> key </identifier>
                      </term>
                      <symbol> = </symbol>
                      <term>
                        <integerConstant> 0 </integerConstant>
                      </term>
                    </expression>
                    <symbol> ) </symbol>
                  </term>
                </term>
              </expression>
              <symbol> ) </symbol>
              <symbol> { </symbol>
              <statements>
                <letStatement>
                  <keyword> let </keyword>
                  <identifier> key </identifier>
                  <symbol> = </symbol>
                  <expression>
                    <term>
                      <identifier> Keyboard </identifier>
                      <symbol> . </symbol>
                      <identifier> keyPressed </identifier>
                      <symbol> ( </symbol>
                      <expressionList>
</expressionList>
                      <symbol> ) </symbol>
                    </term>
                  </expression>
                  <symbol> ; </symbol>
                </letStatement>
                <doStatement>
                  <keyword> do </keyword>
                  <identifier> moveSquare </identifier>
                  <symbol> ( </symbol>
                  <expressionList>
</expressionList>
                  <symbol> ) </symbol>
                  <symbol> ; </symbol>
                </doStatement>
              </statements>
              <symbol> } </symbol>
            </whileStatement>
          </statements>
          <symbol> } </symbol>
        </whileStatement>
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


def test_comments():
    snippet = \
"""
   field Square square; // Comment
   field int direction; // Another Comment
"""

    analyzed = \
"""
 <classVarDec>
    <keyword> field </keyword>
    <identifier> Square </identifier>
    <identifier> square </identifier>
    <symbol> ; </symbol>
  </classVarDec>
  <classVarDec>
    <keyword> field </keyword>
    <keyword> int </keyword>
    <identifier> direction </identifier>
    <symbol> ; </symbol>
  </classVarDec>
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

    def test_return(self):
        actual_string, expected_string = self._prepare_test(*non_void_return())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_two_var_dec(self):
        actual_string, expected_string = self._prepare_test(*class_level_vars())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_two_funcs(self):
        actual_string, expected_string = self._prepare_test(*multiple_funcs())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_let(self):
        actual_string, expected_string = self._prepare_test(*let())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_if(self):
        actual_string, expected_string = self._prepare_test(*if_do())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_while(self):
        actual_string, expected_string = self._prepare_test(*test_while())
        self.assertMultiLineEqual(actual_string, expected_string)

    def test_comments(self):
        actual_string, expected_string = self._prepare_test(*test_comments())
        self.assertMultiLineEqual(actual_string, expected_string)
