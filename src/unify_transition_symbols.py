#!/usr/bin/env python3

# ====================================================
# file name: unify_transition_symbols_except.py
#
# Script to test result of unifying transition symbols of FA except for specific symbols.
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
from collections import deque
from copy import deepcopy
import itertools
import argparse
from optifa import *
#import optifa

# Main script function
def main():
    fa_orig, symbols = parse_args()  # Parse program arguments.

    fa_orig.unify_transition_symbols_except(symbols)
    fa_orig.print_automaton()


def parse_args():
    """Parse arguments using argparse."""
    arg_parser = argparse.ArgumentParser(description='Interpreter of IPPcode21 in XML format.')
    arg_parser.add_argument('fa_a_path', metavar='AUTOMATON', type=str,
                    help='Finate automaton to unify its transition symbols except chosen symbols.')
    arg_parser.add_argument('symbols', nargs='*', metavar='SYMBOL', type=str,
                    help='Symbols to keep.')

    # Test for '--help' argument.
    if '--help' in sys.argv or '-h' in sys.argv:
        arg_parser.print_help()
        sys.exit(0)

    args = arg_parser.parse_args()

    fa_a_orig = symboliclib.parse(args.fa_a_path)

    return fa_a_orig, args.symbols


if __name__ == "__main__":
    main()

# End of file.
