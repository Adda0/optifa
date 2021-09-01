#!/usr/bin/python3

# ====================================================
# file name: remove_comments_from_fa.py
#
# Script to remove all comments from FA for processing given FA with symboliclip for optimizing
# ====================================================
# project: IP1 | Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

import sys

# Main script function
def main():
    #TODO support multiline comments
    file_fa_name = sys.argv[1]
    file_fa_in = open(file_fa_name, 'r')
    file_fa_out = open(file_fa_name + '_no_comments', 'w+')
    in_comment = False
    line = ""
    for line in file_fa_in:
        if '(*' in line:
            in_comment = True
            index = line.find('(*')
            file_fa_out.write(line[:index - 1])
            curr_char = ''
            prev_char = ''
            while index < len(line) and prev_char != '*' and curr_char != ')':
                prev_char = curr_char
                curr_char = line[index]
                index += 1

            if prev_char == '*' and curr_char == ')':
                in_comment = False
                file_fa_out.write(line[index + 1:])

        elif not in_comment:
            file_fa_out.write(line)


if __name__ == "__main__":
    print("Starting prepare_fa.py.")  # DEBUG
    main()
    print("Ending prepare_fa.py.")  # DEBUG

# End of file prepare_fa.py #
