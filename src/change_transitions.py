#!/usr/bin/python3

# file name: change_transitions.py
#
# Script to change transitions of finite automata for lasso automata generation.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

from pathlib import Path
import sys
import symboliclib


# Main script function
def main():
    # names of used files
    fa_name = sys.argv[1]  # automaton file
    fa_name_dest = sys.argv[2]

    try:
        file_fa = open(fa_name, "r")
        file_fa_dest = open(fa_name_dest, "w+")
    except IOError:
        file_name = Path(__file__).name
        print('ERROR: ' + file_name + ': Opening file failed.', sep='', end='\n', file=sys.stderr)
        exit()

    file_fa_dest.write('Ops *:1 x:0\n')

    transitions = False

    while not transitions:
        line = file_fa.readline()
        if line.startswith('Ops'):
            continue
        if line.startswith('Transitions'):
            transitions = True

        file_fa_dest.write(line)

    while transitions:
        line = file_fa.readline()
        if not line:
            break
        if '->' in line and not line.startswith('x -> ') :
            line_split = line.split('(', 2)
            line_split[0] = '*('
            file_fa_dest.write(line_split[0] + line_split[1])
        else:
            file_fa_dest.write(line)

    file_fa.close()
    file_fa_dest.close()


if __name__ == "__main__":
    print("Starting change_transitions.py.")  # DEBUG
    main()
    print("Ending change_transitions.py.")  # DEBUG

# End of file prepare_fa.py #
