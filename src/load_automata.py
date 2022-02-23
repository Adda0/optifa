#!/usr/bin/env -S python3 -u

# ====================================================
# file name: load_automata.py
#
# Script to store parsed objects of given automata into separate files.
# ====================================================
# project: Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

import sys
import symboliclib
from lfa import LFA
from z3 import *
from collections import deque
from copy import deepcopy
import itertools
import argparse
from optifa.basic import *
from dataclasses import dataclass
import pickle

# Main script function.
def main():
    fa_a_orig, fa_b_orig, f_fa_a_loaded, f_fa_b_loaded, unify_symbols = parse_args()  # Parse program arguments.

    if unify_symbols:
        fa_a_orig.unify_transition_symbols(unify_symbols)
        fa_b_orig.unify_transition_symbols(unify_symbols)

    # Store parsed automata objects to separate files.
    pickle.dump(fa_a_orig, f_fa_a_loaded)
    pickle.dump(fa_b_orig, f_fa_b_loaded)

    f_fa_a_loaded.close()
    f_fa_b_loaded.close()

    #fa_a_orig.print_automaton()
    #fa_b_orig.print_automaton()


def parse_args():
    """Parse arguments using argparse."""
    arg_parser = argparse.ArgumentParser(description='Script to store parsed automata objects into separate files.')
    arg_parser.add_argument('-a', metavar='AUTOMATON_A', type=str,
                    help='Automaton A to load.')
    arg_parser.add_argument('-b', metavar='AUTOMATON_B', type=str,
                    help='Automaton B to load.')
    arg_parser.add_argument('--out_a', metavar='AUTOMATON_A_LOADED', type=argparse.FileType('wb'),
                    help='Automaton A object file to store loaded automaton to.')
    arg_parser.add_argument('--out_b', metavar='AUTOMATON_B_LOADED', type=argparse.FileType('wb'),
                    help='Automaton B object file to store loaded automaton to.')
    symbols_group = arg_parser.add_mutually_exclusive_group()
    symbols_group.add_argument('--unify-symbols', '-u', nargs = '*', metavar = 'SYMBOL', type = str, default = [],
                    help = "Symbols to unify.")
    symbols_group.add_argument('--keep-symbols', '-k', nargs = '*', metavar = 'SYMBOL', type = str, default = [],
                    help = "Symbols to keep.")

    # Test for '--help' argument.
    if '--help' in sys.argv or '-h' in sys.argv:
        arg_parser.print_help()
        sys.exit(0)

    #try:
    args = arg_parser.parse_args()
    #except OSError as exception:
    #    print_error(f"{exception.strerror}: {exception.filename}")
    #except:
    #    print_error("Got invalid arguments.")

    fa_a_orig = symboliclib.parse(args.a)
    fa_b_orig = symboliclib.parse(args.b)

    # Symbols to exclude.
    unify_symbols = []
    if args.unify_symbols:
        unify_symbols = args.unify_symbols
    elif args.keep_symbols:
        unify_symbols = (fa_a_orig.alphabet.union(fa_b_orig.alphabet)).difference(args.keep_symbols)

    return fa_a_orig, fa_b_orig, args.out_a, args.out_b, unify_symbols


if __name__ == "__main__":
    main()

# End of file.
