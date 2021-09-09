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
from collections import deque
from copy import deepcopy
import itertools
import argparse

import pickle

import symboliclib
from lfa import LFA
from optifa import *


# Main script function
def main():
    fa_a_orig, fa_b_orig, break_when_final = parse_args()  # Parse program arguments.

    # Run for emptiness test with break_when_final == True or
    # for full product construction with break_when_final == False.
    intersection = fa_a_orig.intersection_count(fa_b_orig, break_when_final)
    print_csv(len(intersection.states))
    print_csv(len(intersection.final))


def parse_args():
    """Parse arguments using argparse."""
    arg_parser = argparse.ArgumentParser(description='Script to generate basic product of two automata.')
    arg_parser.add_argument('--fa_a_loaded', metavar='AUTOMATON_A_LOADED', type=argparse.FileType('rb'),
                    help='Automaton A object file to generate product from.')
    arg_parser.add_argument('--fa_b_loaded', metavar='AUTOMATON_B_LOADED', type=argparse.FileType('rb'),
                    help='Automaton B object file to generate product from.')
    arg_parser.add_argument('--fa_a_path', metavar='AUTOMATON_A', type=str,
                    help='Automaton A to generate product from.')
    arg_parser.add_argument('--fa_b_path', metavar='AUTOMATON_B', type=str,
                    help='Automaton B to generate product from.')
    arg_parser.add_argument('--break_when_final', '-b', action='store_true', default=False,
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

    if args.fa_a_loaded and args.fa_b_loaded:
        fa_a_orig = pickle.load(args.fa_a_loaded)
        fa_b_orig = pickle.load(args.fa_b_loaded)
    elif args.fa_a_path and args.fa_b_path:
        fa_a_orig = symboliclib.parse(args.fa_a_path)
        fa_b_orig = symboliclib.parse(args.fa_b_path)

    return fa_a_orig, fa_b_orig, args.break_when_final


if __name__ == "__main__":
    main()

# End of file.
