import re
import string

from optparse import OptionParser

SPACES_PER_TAB = 4

# Brace types
EGYPTIAN = 'EGYPTIAN'
BLOCK = 'BLOCK'
UNKNOWN = 'UNKNOWN'

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
        re.sub("'\\?[^']'", '', s) for s in eol_stripped
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
        line_to_parse = line[start_index::]
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
        elif not manager.in_comment and '{' in line_to_parse:
            index_in_line = line_to_parse.find('{') + start_index
            indent = len(re.match('^[ ]*', line).group())
            if index_in_line == indent:
                manager.stack.append(StartBrace(BLOCK, line_number, indent))
                if index_in_line + 1 != len(line):
                    parse_line(line, line_number, index_in_line + 1)
            elif index_in_line + 1 == len(line):
                manager.stack.append(StartBrace(EGYPTIAN, line_number, indent))
            else:
                manager.stack.append(StartBrace(UNKNOWN, line_number, index_in_line))
                if index_in_line + 1 != len(line):
                    parse_line(line, line_number, index_in_line + 1)
        elif not manager.in_comment and '}' in line_to_parse:
            index = line_to_parse.find('}') + start_index
            start = manager.stack.pop()
            manager.brace_pairs.append(BracePair(start, line_number, index))
            if index + 1 != len(line):
                parse_line(line, line_number, index + 1)

    for i, line in enumerate(without_comments):
        parse_line(line, i)

    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    parser = OptionParser()
    opts, args = parser.parse_args()

    if len(args) != 1:
        print 'Needs a file!'
    else:
        file = open(args[0])
        get_brace_matching(file)
        
