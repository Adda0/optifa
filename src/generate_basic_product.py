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
from optifa.basic import *
from optifa.program_config import ProductConstructionConfig, ProductConstructionArgumentsParser


# Main script function
def main():
    config = ArgumentsParser.get_config(ProductConstructionConfig)  # Parse program arguments.

    # Run for emptiness test with break_when_final == True or
    # for full product construction with break_when_final == False.
    intersection = config.fa_a_orig.intersection_count(config.fa_b_orig, config.break_when_final)
    print_csv(len(intersection.states))
    print_csv(len(intersection.final))

    # Store product.
    if config.store_product:
        intersection.print_automaton(config.store_product)


class ArgumentsParser(ProductConstructionArgumentsParser):
    def __init__(self):
        super().__init__()

        self.arg_parser.description = 'Construct product (intersection) of two finite automata using basic naive ' \
                                      'product construction algorithm. '


if __name__ == "__main__":
    main()

# End of file.
