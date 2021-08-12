#!/usr/bin/env python3

# ====================================================
# file name: print_automata_sizes.py
#
# Script to print state space sized of two automata.
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
    fa_a_orig, fa_b_orig, fa_a_path, fa_b_path = parse_args()  # Parse program arguments.

    # Print sizes of original automata.
    (larger, smaller) = (fa_a_path, fa_b_path) if len(fa_a_orig.states) > len(fa_b_orig.states) else (fa_b_path, fa_a_path)
    print_data(larger, smaller)


def print_data(larger, smaller):
    print_csv(larger)
    print_csv(smaller)

def parse_args():
    """Parse arguments using argparse."""
    arg_parser = argparse.ArgumentParser(description='Interpreter of IPPcode21 in XML format.')
    arg_parser.add_argument('fa_a_path', metavar='AUTOMATON_A', type=str,
                    help='Automaton A to print its state space size.')
    arg_parser.add_argument('fa_b_path', metavar='AUTOMATON_B', type=str,
                    help='Automaton B to print its state space size.')

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

    return fa_a_orig, fa_b_orig, args.fa_a_path, args.fa_b_path


if __name__ == "__main__":
    main()

# End of file.
