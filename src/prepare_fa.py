#!/usr/bin/python3

# ====================================================
# file name: prepar_fa.py
#
# Script to prepare given finite automata for optimizing
# ====================================================
# project: IP1 | Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

import sys
import symboliclib


# Main script function
def main():
    automaton_name = sys.argv[1]

    fa_a = symboliclib.parse(automaton_name)

    fa_a.unify_transition_symbols()

    fa_a = fa_a.simple_reduce()
    fa_a = fa_a.determinize()
    fa_a.print_automaton('tmp_automaton')
    #fa_a.print_automaton() #DEBUG

if __name__ == "__main__":
    print("Starting prepare_fa.py.")  # DEBUG
    main()
    print("Ending prepare_fa.py.")  # DEBUG

# End of file.
