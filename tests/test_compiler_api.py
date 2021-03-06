
import unittest
from jack_compiler.JackCompiler import JackCompiler
from pathlib import Path

from tests.globals import PROJ_10_DIR

class CompilerSetUpTest(unittest.TestCase):

    def test_valid_filepath_argument(self):
        jack_path = PROJ_10_DIR / "Square/Square.jack"
        compiler = JackCompiler(path=jack_path)
        self.assertTrue(len(compiler.jack_file_paths) == 1, "Expected one path in jack_file_paths list")
        self.assertEqual(compiler.jack_file_paths[0].as_posix(), jack_path.as_posix())

    def test_wrong_filepath_extension(self):
        xml_file_path = PROJ_10_DIR / "Square/Square.xml"
        self.assertRaises(AssertionError, JackCompiler, xml_file_path)

    def test_nonexistent_filepath(self):
        non_existent_path = PROJ_10_DIR / "Square/erehwon.md"
        self.assertRaises(AssertionError, JackCompiler, non_existent_path)

    def test_valid_directory_path_as_argument(self):
        jack_dir = PROJ_10_DIR / "Square"
        expected_jack_paths = list(map(lambda x: jack_dir.as_posix() + "/" + x + ".jack", ["Main", "Square", "SquareGame"]))

        analyzer = JackCompiler(path=Path(jack_dir ))
        actual_jack_paths = sorted([path.as_posix() for path in analyzer.jack_file_paths])
        self.assertListEqual(expected_jack_paths, actual_jack_paths, "contents of 'jack_file_paths' is unexpected.")
