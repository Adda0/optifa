#!/usr/bin/env -S python3 -u

# file name: resolve_satisfiability_variable_length_abstraction.py
#
# Script to run product construction with variable length abstraction.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

import sys
from copy import deepcopy
import itertools
import argparse
from dataclasses import dataclass
import math

import z3

import symboliclib
from lfa import LFA
from optifa.basic import *
from optifa.program_config import ProgramConfig, ProgramArgumentsParser


# Main script function.
def main():
    config = ArgumentsParser.get_config(Config)  # Parse program arguments.
    fa_a_orig = config.fa_a_orig
    fa_b_orig = config.fa_b_orig

    # Add one unified final state
    abstract_final_symbol = 'abstract_final_symbol'
    abstract_final_state = 'abstract_final_state'

    fa_a_orig.add_abstract_final_state(abstract_final_state, abstract_final_symbol)
    fa_b_orig.add_abstract_final_state(abstract_final_state, abstract_final_symbol)

    # Add one unified initial state.
    abstract_initial_symbol = 'abstract_initial_symbol'
    abstract_initial_state = 'abstract_initial_state'

    fa_a_orig.add_abstract_initial_state(abstract_initial_state, abstract_initial_symbol)
    fa_b_orig.add_abstract_initial_state(abstract_initial_state, abstract_initial_symbol)

    fa_a_unified = deepcopy(fa_a_orig)
    fa_b_unified = deepcopy(fa_b_orig)

    if config.unify_symbols:
        fa_a_unified.unify_transition_symbols(config.unify_symbols)
        fa_b_unified.unify_transition_symbols(config.unify_symbols)

    # Run for emptiness test with break_when_final == True or
    # for full product construction with break_when_final == False.

    processed_pair_states_cnt = 0

    # Initialize SMT solver object.
    smt = z3.Solver()
    if config.timeout:
        # print(f"Setting timeout {config.timeout}")
        smt.set("timeout", config.timeout)  # Set solver to timeout after given amount of time in ms.

    add_persistent_formulae(smt, fa_a_unified, fa_b_unified, config)

    # Define additional variables.
    q_checked_pairs = {}
    q_pair_states = deque()

    # Enqueue the initial states.
    for a_initial_state in fa_a_orig.start:
        for b_initial_state in fa_b_orig.start:
            q_pair_states.append([a_initial_state, b_initial_state, False])

    # Generate single handle and loop automata per original input automaton.
    # Therefore, only single handle and loop automaton for all of the tested
    # states in the original automaton is needed.
    intersect_ab = LFA.get_new()

    fa_a_copy = deepcopy(fa_a_orig)
    fa_b_copy = deepcopy(fa_b_orig)

    found = False
    skipped_cnt = 0
    false_cnt = 0
    sat_cnt = 0

    # When there are any pair states to test for satisfiability, test them.
    while q_pair_states:
        # curr_pair = q_pair_states.popleft()  # BFS
        curr_pair = q_pair_states.pop()  # DFS
        product_state_name = curr_pair[0] + ',' + curr_pair[1]

        q_checked_pairs[product_state_name] = True

        fa_a_unified.start = {curr_pair[0]}
        fa_b_unified.start = {curr_pair[1]}
        fa_a_copy.start = {curr_pair[0]}
        fa_b_copy.start = {curr_pair[1]}

        # If the current pair is a single pair created from the previous pair,
        # no need to check for satisfiability.
        # if True:  # Turn Skip feature off.
        if not curr_pair[2]:
            processed_pair_states_cnt += 1

            satisfiable = check_satisfiability(fa_a_unified, fa_b_unified, smt, config)
            if satisfiable:
                sat_cnt += 1
        else:
            satisfiable = True
            # printproduct_state_name + " sat", end='  ')
            skipped_cnt += 1

        if satisfiable:
            # Add product states to intersection FA.
            intersect_ab.states.add(product_state_name)
            if product_state_name not in intersect_ab.transitions:
                intersect_ab.transitions[product_state_name] = {}

            if curr_pair[0] in fa_a_orig.final and curr_pair[1] in fa_b_orig.final:
                # Automata have a non-empty intersection. We can end the testing here as we have found a solution.
                intersect_ab.final.add(product_state_name)
                found = True
                if config.break_when_final:
                    break

            # print(q_pair_states)
            # old_pair_states_len = len(q_pair_states)

            # Generate the following potential product-states.
            make_pairs(fa_a_orig, fa_b_orig, q_pair_states, q_checked_pairs, intersect_ab, curr_pair)

            # pair_states_len_diff = len(q_pair_states) - old_pair_states_len
            # print(pair_states_len_diff)
            # print(q_pair_states)
        else:
            false_cnt += 1

        # printlen(q_pair_states))

    intersect_ab.start = {f"{abstract_initial_state},{abstract_initial_state}"}
    intersect_ab.remove_useless_transitions()
    intersect_ab.remove_abstract_final_state(abstract_final_symbol, abstract_final_state)
    intersect_ab.remove_abstract_initial_state(abstract_initial_symbol, abstract_initial_state)
    # Output format: <checked> <processed> <sat> <false_cnt> <skipped>.. <intersect_states> <final_cnt>
    print_csv(len(q_checked_pairs))
    print_csv(processed_pair_states_cnt)
    print_csv(sat_cnt)
    print_csv(false_cnt)
    print_csv(skipped_cnt)
    print_csv(len(intersect_ab.states))
    print_csv(len(intersect_ab.final))
    # print(intersect_ab.transitions)
    # intersect_ab.print_automaton()
    # print(intersect_ab.final)

    # Store product.
    if config.store_product:
        intersect_ab.print_automaton(config.store_product)


def check_satisfiability(fa_a, fa_b, smt, config):
    """
    Check satisfiability for formulae and Parikh image using SMT solver Z3.
    :param fa_a: First automaton.
    :param fa_b: Second automaton.
    :param fa_a_formulae_dict: Dictionary with formulae for FA A.
    :param fa_b_formulae_dict: Dictionary with formulae for FA B.
    :param config: Program configuration.
    :return: True if satisfiable; False if not satisfiable.
    """

    if next(iter(fa_a.start)) in fa_a.final and next(iter(fa_b.start)) in fa_b.final:
        # printnext(iter(fa_a.start)) + ',' + next(iter(fa_b.start)) + " final", end='  ')
        # print('final')
        return True

    # Add clauses – conjunction of formulae.
    smt.push()
    add_state_specific_formulae(smt, fa_a, fa_b, config)

    # Check for satisfiability.
    # print("start smt check")
    res = smt.check()
    # print(res)

    smt.pop()

    if res != z3.unsat:  # ~ res in [z3.sat, z3.unknown].
        # printnext(iter(fa_a.start)) + ',' + next(iter(fa_b.start)) + " true", end='  ')
        # print("true", end='  ')
        # print(smt.model())
        return True

    # printnext(iter(fa_a.start)) + ',' + next(iter(fa_b.start)) + " false", end='  ')
    # print("false")
    return False


class ArgumentsParser(ProgramArgumentsParser):
    def __init__(self):
        super().__init__()

        # Set additional arguments.
        self.arg_parser.add_argument('--forward-lengths', '-f', action='store_true',
                                     help="Compute forward lengths 'z' for Parikh image.")
        self.arg_parser.add_argument('--no-z-constraints', '-z', action='store_true',
                                     help='Compute formulae without constraints for connectivity of automaton.')
        self.arg_parser.add_argument('--timeout', '-t', metavar='TIMEOUT_MS', type=int,
                                     help='Set timeout after TIMEOUT_MS ms for Z3 SMT solver.')

        symbols_group = self.arg_parser.add_mutually_exclusive_group()
        symbols_group.add_argument('--unify-symbols', '-u', nargs='*', metavar='SYMBOL', type=str, default=[],
                                   help="Symbols to unify.")
        symbols_group.add_argument('--keep-symbols', '-k', nargs='*', metavar='SYMBOL', type=str, default=[],
                                   help="Symbols to keep.")


class Config(ProgramConfig):
    """Class for storing program configurations passed as command line arguments."""

    def __init__(self, args):
        super().__init__(args)

        self.reverse_lengths = not args.forward_lengths
        self.use_z_constraints = not args.no_z_constraints
        self.timeout = args.timeout

        # Symbols to exclude.
        self.unify_symbols = []
        if args.unify_symbols:
            self.unify_symbols = args.unify_symbols
        elif args.keep_symbols:
            self.unify_symbols = (self.fa_a_orig.alphabet.union(self.fa_b_orig.alphabet)).difference(args.keep_symbols)


if __name__ == "__main__":
    main()

# End of file.
