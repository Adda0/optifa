#!/usr/bin/python3

# file name: determinize_fa.py
#
# Script to determinize given finite automaton, storing its determinized result to
# for optimizing
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

import sys
sys.path.append('/mnt/DATA/Data/David/School/projPrax/symboliclib/symboliclib/') #DEBUG
import symboliclib


# Main script function
def main():
    automaton_name = sys.argv[1]  # file with the FA to be determinized
    automaton_name_dest = sys.argv[2]  # file to store the determinized automaton
    print('Starting determinize_fa.py for automaton: ' + automaton_name + '.')  # DEBUG
    fa_a = symboliclib.parse(automaton_name)
    fa_a = fa_a.simple_reduce()
    fa_a = fa_a.determinize()
    label = fa_a.label
    #fa_a.print_automaton() #DEBUG
    fa_a.print_automaton(automaton_name_dest)


if __name__ == "__main__":
    main()
    print('Ending determinize_fa.py.')  # DEBUG

# End of file prepare_fa.py #
