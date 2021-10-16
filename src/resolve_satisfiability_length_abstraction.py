#!/usr/bin/env -S python3 -u

# ====================================================
# file name: resolve_satisfiability.py
#
# Script to resolve satisfiable of given formulae using Z3 SMT solver.
# ====================================================
# project: Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

from collections import deque
from copy import deepcopy
import itertools

from lfa import LFA
from optifa import *


# Main script function.
def main():
    config = ArgumentParser.get_config(Config)  # Parse program arguments.
    fa_a_orig = config.fa_a_orig
    fa_b_orig = config.fa_b_orig

    # Run for emptiness test with break_when_final == True or
    # for full product construction with break_when_final == False.

    processed_pair_states_cnt = 0

    q_checked_pairs = {}
    q_pair_states = deque()

    # Enqueue the initial states.
    for a_initial_state in fa_a_orig.start:
        for b_initial_state in fa_b_orig.start:
            q_pair_states.append([a_initial_state, b_initial_state, False])

    # Generate single handle and loop automata per original input automaton.
    # Therefore, only single handle and loop automaton for all of the tested
    # states in the original automaton is needed.
    fa_a_handle_and_loop = LFA.get_new()
    fa_b_handle_and_loop = LFA.get_new()
    intersect_ab = LFA.get_new()

    fa_a_unified = deepcopy(fa_a_orig)
    fa_b_unified = deepcopy(fa_b_orig)

    fa_a_unified.unify_transition_symbols()
    fa_b_unified.unify_transition_symbols()

    found = False
    skipped_cnt = 0
    false_cnt = 0
    sat_cnt = 0

    # When there are any pair states to test for satisfiability, test them.
    while q_pair_states:
        #curr_pair = q_pair_states.popleft()  # BFS
        curr_pair = q_pair_states.pop()  # DFS
        product_state_name = curr_pair[0] + ',' + curr_pair[1]
        q_checked_pairs[product_state_name] = True

        # If the current pair is a single pair created from the previous pair,
        # no need to check for satisfiability.
        #if True:  # Turn Skip feature off.
        if not curr_pair[2]:
            processed_pair_states_cnt += 1

            fa_a_unified.start = {curr_pair[0]}
            fa_b_unified.start = {curr_pair[1]}

            fa_a_unified.determinize_check(fa_a_handle_and_loop)
            fa_b_unified.determinize_check(fa_b_handle_and_loop)

            if not fa_a_handle_and_loop.final or not fa_b_handle_and_loop.final:
                break

            fa_a_formulae_dict = fa_a_handle_and_loop.count_formulae_for_lfa()
            #print(fa_a_formulae_dict)  # DEBUG
            fa_b_formulae_dict = fa_b_handle_and_loop.count_formulae_for_lfa()
            #print(fa_b_formulae_dict)  # DEBUG

            satisfiable = check_length_satisfiability(config, fa_a_formulae_dict, fa_b_formulae_dict)
            if satisfiable:
                sat_cnt += 1
        else:
            satisfiable = True
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

            #print(q_pair_states)
            #old_pair_states_len = len(q_pair_states)

            # Generate the following potential product-states.
            make_pairs(fa_a_orig, fa_b_orig, q_pair_states, q_checked_pairs, intersect_ab, curr_pair)

            #pair_states_len_diff = len(q_pair_states) - old_pair_states_len
            #print(pair_states_len_diff)
            #print(q_pair_states)
        else:
            false_cnt += 1

    intersect_ab.remove_useless_transitions()
    # Output format: <checked> <processed> <sat> <skipped> <false_cnt> <intersect> <final_cnt>
    print_csv(len(q_checked_pairs))
    print_csv(processed_pair_states_cnt)
    print_csv(sat_cnt)
    print_csv(false_cnt)
    print_csv(skipped_cnt)
    if len(fa_a_orig.states) > len(fa_b_orig.states):
        print_csv(len(fa_a_handle_and_loop.states))
        print_csv(len(fa_b_handle_and_loop.states))
    else:
        print_csv(len(fa_b_handle_and_loop.states))
        print_csv(len(fa_a_handle_and_loop.states))
    print_csv(len(intersect_ab.states))
    print_csv(len(intersect_ab.final))
    #print(intersect_ab.transitions)
    #intersect_ab.print_automaton()
    #print(intersect_ab.final)


class ArgumentParser(ProgramArgumentParser):
    def __init__(self):
        super().__init__()

        # Set additional arguments.
        self.arg_parser.add_argument('--smt', '-s', action='store_true',
                                     help='Use SMT solver Z3 to check for satisfiability of formulae.')
        self.arg_parser.add_argument('--timeout', '-t', metavar='TIMEOUT_MS', type=int,
                                     help='Set timeout after TIMEOUT_MS ms for Z3 SMT solver.')


class Config(ProgramConfig):
    """Class for storing program configurations passed as command line arguments."""

    def __init__(self, args):
        super().__init__(args)

        self.smt_free = not args.smt
        self.timeout = args.timeout


if __name__ == "__main__":
    main()

# End of file.
