#!/usr/bin/env python3

# ====================================================
# file name: generate_basic_product.py
#
# Script to generate basic product of two automata.
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

# Main script function
def main():
    fa_a_orig, fa_b_orig, break_when_final = parse_args()  # Parse program arguments.

    A_larger = True
    # Print sizes of original automata.
    if len(fa_a_orig.states) > len(fa_b_orig.states):
        print(len(fa_a_orig.states), end=' ')
        print(len(fa_b_orig.states), end=' ')
    else:
        A_larger = False
        print(len(fa_b_orig.states), end=' ')
        print(len(fa_a_orig.states), end=' ')

    # Run only once: for emptiness test (break_when_final == True) or
    # for full product construction (break_when_final == False).
    intersection = fa_a_orig.intersection_count(fa_b_orig, break_when_final)
    print('')
    print('N', end=' ')
    print(len(intersection.states), end=' ')
    print(len(intersection.final), end=' ')
    print()


def parse_args():
    """Parse arguments using argparse."""
    arg_parser = argparse.ArgumentParser(description='Interpreter of IPPcode21 in XML format.')
    arg_parser.add_argument('fa_a_path', metavar='AUTOMATON_A', type=str,
                    help='Automaton A to generate product from.')
    arg_parser.add_argument('fa_b_path', metavar='AUTOMATON_B', type=str,
                    help='Automaton B to generate product from.')
    arg_parser.add_argument('--break_when_final', action='store_true', default=False,
                    help='Break when final state is encountered to execute emptiness test.')

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

    fa_a_orig = symboliclib.parse(args.fa_a_path)
    fa_b_orig = symboliclib.parse(args.fa_b_path)

    return fa_a_orig, fa_b_orig, args.break_when_final


def print_error(message, err_code=1):
    """
    Print error message and end the program.
    :param message: Error message to be printed.
    :param err_code: Error code to end the program with.
    """
    print('ERROR: ' + __file__ + ': ' + message, file=sys.stderr)
    sys.exit(err_code)


if __name__ == "__main__":
    main()

# End of file.
