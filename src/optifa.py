#!/usr/bin/env python3

# ====================================================
# file name: optifa.py
#
# Optimizing Automata Product Construction and Emptiness Test base class.
# ====================================================
# project: Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

#import os
import sys
from collections import deque
import itertools
#from copy import deepcopy
import argparse

import pickle
import z3
from z3 import And, Int, Or, Sum

#import symboliclib
#from lfa import LFA


def print_csv(message):
    """
    Print message in a comma separated values format.
    :param message: Message to be printed.
    """
    print(message, end=',')

class Optifa_a:
    """Optimizing Automata Product Construction and Emptiness Test base class"""

    @staticmethod
    def print_error(message, err_code=1):
        """
        Print error message and end the program.
        :param message: Error message to be printed.
        :param err_code: Error code to end the program with.
        """
        print('ERROR: ' + __file__ + ': ' + message, file=sys.stderr)
        sys.exit(err_code)


def make_pairs(fa_a_orig, fa_b_orig, q_pair_states, q_checked_pairs, intersect, curr_state, single_pair = False):
    a_state = curr_state[0]
    b_state = curr_state[1]
    product_state_name = a_state + ',' + b_state

    new_pairs = deque()
    new_pairs_cnt = 0

    if a_state in fa_a_orig.transitions and b_state in fa_b_orig.transitions:
        for label in fa_a_orig.transitions[a_state]:
            if label in fa_b_orig.transitions[b_state]:
                endstates = itertools.product(fa_a_orig.transitions[a_state][label], fa_b_orig.transitions[b_state][label])
                for endstate in endstates:
                    endstate_str = endstate[0] + "," + endstate[1]

                    if label not in intersect.transitions[product_state_name]:
                        intersect.transitions[product_state_name][label] = [endstate_str]
                        intersect.alphabet.add(str(label))
                    else:
                        intersect.transitions[product_state_name][label].append(endstate_str)

                    new_pairs_cnt += 1
                    if endstate_str not in q_checked_pairs:
                        new_pairs.append(endstate)

    # If only a single new product state was generated, set this state as skippable.
    if new_pairs_cnt == 1:
        single_pair = True

    # Append new product states to work set, optionally update the work set elements.
    for new_pair in new_pairs:
        # Add state to checked states.
        q_checked_pairs[new_pair[0] + ',' + new_pair[1]] = True

        if [new_pair[0], new_pair[1], True] in q_pair_states:
            pass
        elif [new_pair[0], new_pair[1], False] in q_pair_states and single_pair:
            id = q_pair_states.index([new_pair[0], new_pair[1], False])
            q_pair_states[id][2] = True
        else:
            q_pair_states.append([new_pair[0], new_pair[1], single_pair])


def enqueue_next_states(q_states, fa_orig, curr_state):
    transitions = fa_orig.get_deterministic_transitions(curr_state)

    for trans_symbol in transitions:
        for state_dict_elem in transitions[trans_symbol]:
            for state in state_dict_elem.split(','):
                q_states.append(state)

def add_persistent_formulae(smt, fa_a_orig, fa_b_orig, config):
    # Add persistent formulae valid for every product-state.

    # FA A: First conjunct.
    for state in fa_a_orig.states:
        smt.add(Int('a_u_%s' % state) + Sum([Int('a_y_%s' % transition) for transition in fa_a_orig.get_ingoing_transitions_names(state)]) - Sum([Int('a_y_%s' % transition) for transition in fa_a_orig.get_outgoing_transitions_names(state)]) == 0)

    # FA B: First conjunct.
    for state in fa_b_orig.states:
        smt.add(Int('b_u_%s' % state) + Sum([Int('b_y_%s' % transition) for transition in fa_b_orig.get_ingoing_transitions_names(state)]) - Sum([Int('b_y_%s' % transition) for transition in fa_b_orig.get_outgoing_transitions_names(state)]) == 0)

    # FA A: Second conjunct.
    smt.add( And( [ Int('a_y_%s' % transition) >= 0 for transition in fa_a_orig.get_transitions_names() ] ))

    # FA B: Second conjunct.
    smt.add( And( [ Int('b_y_%s' % transition) >= 0 for transition in fa_b_orig.get_transitions_names() ] ))

    # FA A: Third conjunct.
    for symbol in fa_a_orig.alphabet:
        smt.add(Int('hash_%s' % symbol) == Sum([Int('a_y_%s' % transition) for transition in fa_a_orig.get_transitions_names_with_symbol(symbol)]))

    # FA B: Third conjunct.
    for symbol in fa_b_orig.alphabet:
        smt.add(Int('hash_%s' % symbol) == Sum([Int('b_y_%s' % transition) for transition in fa_b_orig.get_transitions_names_with_symbol(symbol)]))

    if config.reverse_lengths:
        if config.use_z_constraints:
            # FA A: Fourth conjunct.
            for state in fa_a_orig.states:
                if state in fa_a_orig.final:
                    smt.add(Int('a_z_%s' % state) == 1)
                    smt.add(And( [ Int('a_y_%s' % transition) >= 0 for transition in fa_a_orig.get_outgoing_transitions_names(state) ] ))

                if state not in fa_a_orig.start and state not in fa_a_orig.final:
                    smt.add(Or(And( And( Int('a_z_%s' % state) == 0 ) , And( [ Int('a_y_%s' % transition) == 0 for transition in fa_a_orig.get_ingoing_transitions_names(state) ] ) ), Or( [ And( Int('a_y_%s' % transition) >= 0 , Int('a_z_%s' % transition.split('_')[0]) > 0, Int('a_z_%s' % state) == Int('a_z_%s' % transition.split('_')[0]) - 1) for transition in fa_a_orig.get_ingoing_transitions_names(state) ] )))

            # FA B: Fourth conjunct.
            for state in fa_b_orig.states:
                if state in fa_b_orig.final:
                    smt.add(Int('b_z_%s' % state) == 1)
                    smt.add(And( [ Int('b_y_%s' % transition) >= 0 for transition in fa_b_orig.get_outgoing_transitions_names(state) ] ))

                if state not in fa_b_orig.start and state not in fa_a_orig.final:
                    smt.add(Or(And( And( Int('bz_%s' % state) == 0 ) , And( [ Int('b_y_%s' % transition) == 0 for transition in fa_b_orig.get_ingoing_transitions_names(state) ] ) ), Or( [ And( Int('b_y_%s' % transition) >= 0 , Int('b_z_%s' % transition.split('_')[0]) > 0, Int('b_z_%s' % state) == Int('b_z_%s' % transition.split('_')[0]) - 1) for transition in fa_b_orig.get_ingoing_transitions_names(state) ] )))

    # End of SMT formulae initialization.


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

        self.break_when_final = args.break_when_final
        self.store_product = args.store_product


class ProgramArgumentParser:
    """Class parsing arguments using argparse."""

    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(
            description = 'Construct product (intersection) of two finite automata using abstraction optimization techniques.'
        )

        automata_format_group = self.arg_parser.add_mutually_exclusive_group(required = True)
        automata_format_group.add_argument('--loaded', '-l', action = 'store_true',
                        help = 'Read the automata files as a loaded Python objects parsed by Symboliclib.')
        automata_format_group.add_argument('--path', '-p', action = 'store_true',
                        help = 'Read the automata files as a Timbuk format files ready to be parsed by Symboliclib.')

        automata_path_group = self.arg_parser.add_argument_group(title = "Automata to work with", description = "The automata paths for automata to generate product from.")
        automata_path_group.add_argument('--fa-a', '-a', metavar = 'AUTOMATON_A', type = str, required = True,
                        help = 'Automaton A to generate product from.')
        automata_path_group.add_argument('--fa-b', '-b', metavar = 'AUTOMATON_B', type = str, required = True,
                        help = 'Automaton B to generate product from.')

        self.arg_parser.add_argument('--break-when-final', '-r', action = 'store_true',
                        help = 'Break when final state is encountered to execute emptiness test.')
        self.arg_parser.add_argument('--store-product', '-o', metavar = 'PRODUCT_FILE', type = str,
                        help = 'Store generated product into a file PRODUCT_FILE.')

    def test_for_help(self):
        """Test for '--help' argument and print argparse help message when present."""
        if '--help' in sys.argv or '-h' in sys.argv:
            self.arg_parser.print_help()
            sys.exit(0)

    def parse_args(self):
        """Parse program command line arguments."""
        #try:
        args = self.arg_parser.parse_args()
        #except OSError as exception:
        #    print_error(f"{exception.strerror}: {exception.filename}")
        #except:
        #    print_error("Got invalid arguments.")

        self.test_for_help()
        return self.arg_parser.parse_args()


# End of file.
