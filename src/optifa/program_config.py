#!/usr/bin/env python3

# file name: program_config.py
#
# Basic program config.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

import argparse

import pickle

import symboliclib
from lfa import LFA


class ProgramConfig:
    """Class for storing program configurations passed as command line arguments."""

    def __init__(self, args):
        if args.loaded:
            with open(args.fa_a, 'rb') as fa_a, open(args.fa_b, 'rb') as fa_b:
                self.fa_a_orig = pickle.load(fa_a)
                self.fa_b_orig = pickle.load(fa_b)
        elif args.path:
            self.fa_a_orig = symboliclib.parse(args.fa_a)
            self.fa_b_orig = symboliclib.parse(args.fa_b)
        else:
            raise ValueError("missing automata arguments or their wrong combination")



class ProgramArgumentsParser:
    """Class parsing program arguments using argparse."""

    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(description='Prepare two finite automata.')

        automata_format_group = self.arg_parser.add_mutually_exclusive_group(required=True)
        automata_format_group.add_argument('--loaded', '-l', action='store_true',
                                           help='Read the automata files as a loaded Python objects parsed by '
                                                'Symboliclib.')
        automata_format_group.add_argument('--path', '-p', action='store_true',
                                           help='Read the automata files as a Timbuk format files ready to be parsed '
                                                'by Symboliclib.')

        automata_path_group = self.arg_parser.add_argument_group(title="Automata to work with",
                                                                 description="The automata paths for automata to "
                                                                             "generate product from.")
        automata_path_group.add_argument('--fa-a', '-a', metavar='AUTOMATON_A', type=str, required=True,
                                         help='Automaton A to generate product from.')
        automata_path_group.add_argument('--fa-b', '-b', metavar='AUTOMATON_B', type=str, required=True,
                                         help='Automaton B to generate product from.')

    def parse_args(self):
        """Parse program command line arguments."""
        args = self.arg_parser.parse_args()
        return args

    @classmethod
    def get_config(cls, config_class):
        arg_parser = cls()

        # Create Config from the command line arguments.
        return config_class(arg_parser.parse_args())


class ProductConstructionArgumentsParser(ProgramArgumentsParser):
    def __init__(self):
        super().__init__()

        self.arg_parser.description = 'Construct product (intersection) of two finite automata.'

        # Set additional arguments.
        self.arg_parser.add_argument('--break-when-final', '-r', action='store_true',
                                     help='Break when final state is encountered to execute emptiness test.')
        self.arg_parser.add_argument('--store-result', '-o', metavar='RESULT_FILE', type=str,
                                     help='Store result into a file.')


class ProductConstructionConfig(ProgramConfig):
    """Class for storing program configurations passed as command line arguments for product construction algorithms."""

    def __init__(self, args):
        super().__init__(args)

        self.break_when_final = args.break_when_final
        self.store_result = args.store_result
