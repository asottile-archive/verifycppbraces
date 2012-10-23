import re
import string
import sys

from optparse import OptionParser

SPACES_PER_TAB = 4

# Brace types
EGYPTIAN = 'EGYPTIAN'
BLOCK = 'BLOCK'
INITIALIZER = 'INITIALIZER'
UNKNOWN = 'UNKNOWN'

INDENT = re.compile('^[ ]*')

class StartBrace:
    def __init__(self, brace_type, line_number, index):
        self.brace_type = brace_type
        self.line_number = line_number
        self.index = index

class BracePair:
    def __init__(self, start_brace, end_line_number, end_index):
        self.start_brace = start_brace
        self.end_line_number = end_line_number
        self.end_index = end_index

class Manager:
    def __init__(self):
        self.stack = []
        self.brace_pairs = []
        self.in_comment = False

def get_brace_matching(file):
    '''Gets the matchings of braces.

    Args:
        file - Either a file, or an iterable of lines.
    '''

    tabs_adjusted = (
        string.replace(s, '\t', ' ' * SPACES_PER_TAB) for s in file
    )

    eol_stripped = (
        string.rstrip(s) for s in tabs_adjusted
    )

    # XXX: I am pretty sure these removals are not quite correct

    # Remove character literals
    without_chars = (
        re.sub("'\\\\?[^']'", '', s) for s in eol_stripped
    )
    
    # Remove string literals
    without_strings = (
        re.sub('".*(((\\\\\\\\)+")|([^\\\\]"))', '', s) for s in without_chars
    )

    # Remove one line comments
    without_comments = (
        re.sub('//.*$', '', s) for s in without_strings
    )

    manager = Manager()

    def parse_line(line, line_number, start_index=0):
        if start_index >= len(line):
            return

        # rstrip for lines like if (herp) { // blah
        line_to_parse = string.rstrip(line[start_index::])
        starting_index = line_to_parse.find('{')
        if starting_index >= 0:
            starting_index += start_index
        ending_index = line_to_parse.find('}')
        if ending_index >= 0:
            ending_index += start_index

        if manager.in_comment and '*/' in line_to_parse:
            manager.in_comment = False
            end_pos = line_to_parse.find('*/') + start_index + 2
            parse_line(line, line_number, end_pos)
        elif not manager.in_comment and '/*' in line_to_parse:
            # First parse the first part of the line
            index_of_start = line_to_parse.find('/*') + start_index + 2
            parse_line(line[:index_of_start - 2:], line_number, start_index)
            manager.in_comment = True
            # Then parse the rest of the line
            parse_line(line, line_number, index_of_start)
        elif (
            not manager.in_comment and
            starting_index >= 0 and
            (ending_index < 0 or starting_index < ending_index)
        ):
            indent = len(INDENT.match(line).group())
            if starting_index == indent:
                manager.stack.append(StartBrace(BLOCK, line_number, indent))
                parse_line(line, line_number, starting_index + 1)
            elif starting_index + 1 == len(line):
                manager.stack.append(StartBrace(EGYPTIAN, line_number, indent))
            elif (
                (len(manager.stack) and manager.stack[-1].brace_type == INITIALIZER) or
                (starting_index - 1 >= 0 and line[starting_index - 1] == '=') or
                (starting_index - 2 >= 0 and line[starting_index - 2] == '=')
            ):
                manager.stack.append(StartBrace(INITIALIZER, line_number, starting_index))
                parse_line(line, line_number, starting_index + 1)
            else:
                manager.stack.append(StartBrace(UNKNOWN, line_number, starting_index))
                parse_line(line, line_number, starting_index + 1)
        elif not manager.in_comment and ending_index >= 0:
            start = manager.stack.pop()
            manager.brace_pairs.append(BracePair(start, line_number, ending_index))
            parse_line(line, line_number, ending_index + 1)

    for i, line in enumerate(without_comments):
        parse_line(line, i + 1)

    return manager.brace_pairs

def validate_brace_pairs(brace_pairs):

    brace_counts = {
        EGYPTIAN: 0,
        BLOCK: 0,
        INITIALIZER: 0,
        UNKNOWN: 0,
    }

    for brace_pair in brace_pairs:
        brace_counts[brace_pair.start_brace.brace_type] += 1

        if brace_pair.start_brace.brace_type == UNKNOWN:
            for line_number in [brace_pair.start_brace.line_number, brace_pair.end_line_number]:
                print '%s:%s: %s [%s] [%d]' % (
                    'upload.cpp',
                    line_number,
                    'Unknown brace type (probably bad brace)',
                    'Braces',
                    100
                )

        if (
            brace_pair.start_brace.brace_type != INITIALIZER and
            brace_pair.start_brace.index != brace_pair.end_index
        ):
            for line_number in [brace_pair.start_brace.line_number, brace_pair.end_line_number]:
                print '%s:%s: %s [%s] [%d]' % (
                    'upload.cpp',
                    line_number,
                    'Mismatched brace index -- start %s end %s' % (brace_pair.start_brace.index, brace_pair.end_index),
                    'Braces',
                    100
                )

    if bool(brace_counts[EGYPTIAN]) == bool(brace_counts[BLOCK]):
        print '%s:%s: %s [%s] [%d]' % (
            'upload.cpp',
            0,
            'Inconsistent braces in file.  %s egyptian, %s block' % (brace_counts[EGYPTIAN], brace_counts[BLOCK]),
            'Braces',
            100
        )

if __name__ == '__main__':
    parser = OptionParser()
    opts, args = parser.parse_args()

    if len(args) != 1:
        print 'Needs a file!'
    else:
        if args[0] == '-':
          file = sys.stdin
        else:
          file = open(args[0])
        validate_brace_pairs(get_brace_matching(file))
        
