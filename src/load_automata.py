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

import os
import sys
import symboliclib
from lfa import LFA
from z3 import *
from collections import deque
from copy import deepcopy
import itertools
import argparse
from optifa import *
from dataclasses import dataclass
import pickle

# Main script function.
def main():
    fa_a_orig, fa_b_orig, f_fa_a_loaded, f_fa_b_loaded = parse_args()  # Parse program arguments.

    # Store parsed automata objects to separate files.
    pickle.dump(fa_a_orig, f_fa_a_loaded)
    pickle.dump(fa_b_orig, f_fa_b_loaded)

    f_fa_a_loaded.close()
    f_fa_b_loaded.close()


def parse_args():
    """Parse arguments using argparse."""
    arg_parser = argparse.ArgumentParser(description='Script to store parsed automata objects into separate files.')
    arg_parser.add_argument('-a', metavar='AUTOMATON_A', type=str,
                    help='Automaton A to generate product from.')
    arg_parser.add_argument('-b', metavar='AUTOMATON_B', type=str,
                    help='Automaton B to generate product from.')
    arg_parser.add_argument('--out_a', metavar='AUTOMATON_A_LOADED', type=argparse.FileType('wb'),
                    help='Automaton A object file to generate product from.')
    arg_parser.add_argument('--out_b', metavar='AUTOMATON_B_LOADED', type=argparse.FileType('wb'),
                    help='Automaton B object filet o generate product from.')

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

    return fa_a_orig, fa_b_orig, args.out_a, args.out_b


if __name__ == "__main__":
    main()

# End of file.
