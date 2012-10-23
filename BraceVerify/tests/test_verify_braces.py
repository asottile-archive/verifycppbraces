import os.path
import unittest

from brace_verify import get_brace_matching
from brace_verify import BLOCK
from brace_verify import EGYPTIAN
from brace_verify import UNKNOWN

RESOURCES_DIR = 'tests/resources'

class TestFile:
    '''Base class to test a cpp file.'''

    # Set this to the cpp file you are testing.
    filename = None

    def assert_braces_correct(self, braces):
        '''Implement to verify braces!'''
        raise NotImplementedError

    def test_file(self):
        assert(self.filename)
        with open(os.path.join(RESOURCES_DIR, self.filename)) as file:
            braces = get_brace_matching(file)
            self.assert_braces_correct(braces)

class TestBad(unittest.TestCase, TestFile):
    filename='bad.cpp'

    def assert_braces_correct(self, braces):
        for brace in braces:
            self.assertNotEqual(brace.start_brace.index, brace.end_index)

class TestBlock(unittest.TestCase, TestFile):
    filename = 'block.cpp'

    def assert_braces_correct(self, braces):
        for brace in braces:
            self.assertEqual(brace.start_brace.brace_type, BLOCK)
            self.assertEqual(brace.start_brace.index, brace.end_index)

class TestBracesInCharacter(TestBlock):
    filename = 'braces_in_character.cpp'

class TestBracesInCommentBlock(TestBlock):
    filename = 'braces_in_comment_block.cpp'

class TestBracesInCommentLine(TestBlock):
    filename = 'braces_in_comment_line.cpp'

class TestBracesInString(TestBlock):
    filename = 'braces_in_string.cpp'

class TestTabs(TestBlock):
    filename = 'tabs.cpp'

class TestMixedTabs(TestBlock):
    filename = 'mixed_tabs.cpp'

class TestEgyptian(unittest.TestCase, TestFile):
    filename = 'egyptian.cpp'

    def assert_braces_correct(self, braces):
        for brace in braces:
            self.assertEqual(brace.start_brace.index, brace.end_index)
            self.assertEqual(brace.start_brace.brace_type, EGYPTIAN)

class TestMixed(unittest.TestCase, TestFile):
    filename = 'mixed.cpp'

    def assert_braces_correct(self, braces):
        self.assertEqual(braces[0].start_brace.brace_type, BLOCK)
        self.assertEqual(braces[1].start_brace.brace_type, EGYPTIAN)
        for brace in braces:
            self.assertEqual(brace.start_brace.index, brace.end_index)

class TestLinesAndCols(unittest.TestCase, TestFile):
    filename = 'egyptian.cpp'

    def assert_braces_correct(self, braces):
        self.assertEqual(braces[0].start_brace.line_number, 7)
        self.assertEqual(braces[0].end_line_number, 9)
        self.assertEqual(braces[0].start_brace.index, 4)
        self.assertEqual(braces[0].end_index, 4)
        self.assertEqual(braces[1].start_brace.line_number, 5)
        self.assertEqual(braces[1].end_line_number, 12)
        self.assertEqual(braces[1].start_brace.index, 0)
        self.assertEqual(braces[1].end_index, 0)

class TestArrayInit(unittest.TestCase, TestFile):
    filename = 'array_init.cpp'

    def assert_braces_correct(self, braces):
        self.assertEqual(len(braces), 2)

if __name__ == '__main__':
    unittest.main()
