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

import os
import sys
from collections import deque
from copy import deepcopy
import itertools
import argparse

import pickle
from z3 import *

import symboliclib
from lfa import LFA
from optifa import *


# Main script function.
def main():
    fa_a_orig, fa_b_orig, break_when_final, reverse_lengths, use_z_constraints = parse_args()  # Parse program arguments.

    A_larger = True if len(fa_a_orig.states) > len(fa_b_orig.states) else False


    # Add one unified final state
    abstract_final_symbol = 'abstract_final_symbol'
    abstract_final_state = 'abstract_final_state'

    fa_a_orig.alphabet.add(abstract_final_symbol)
    fa_b_orig.alphabet.add(abstract_final_symbol)

    fa_a_orig.states.add(abstract_final_state)
    for final_state in fa_a_orig.final:
        if final_state not in fa_a_orig.transitions.keys():
            fa_a_orig.transitions[final_state] = {}
        fa_a_orig.transitions[final_state][abstract_final_symbol] = [abstract_final_state]
    fa_a_orig.final = set([abstract_final_state])

    fa_b_orig.states.add(abstract_final_state)
    for final_state in fa_b_orig.final:
        if final_state not in fa_b_orig.transitions.keys():
            fa_b_orig.transitions[final_state] = {}
        fa_b_orig.transitions[final_state][abstract_final_symbol] = [abstract_final_state]
    fa_b_orig.final = set([abstract_final_state])

    # Run for emptiness test with break_when_final == True or
    # for full product construction with break_when_final == False.
    processed_pair_states_cnt = 0


    # Initialize SMT solver object.
    smt = Solver()
    # Add persistent formulae valid for every product-state.
    # Create lists of variables for conjunction of formulae.
    hash_phi = [ Int('hash_%s' % symbol) for symbol in fa_a_orig.alphabet ]  # Both FA A and FA B: hash_phi.

    # FA A and FA B variables.
    fa_a_transitions_names = fa_a_orig.get_transitions_names()
    a_y_t = [ Int('a_y_%s' % transition) for transition in fa_a_transitions_names ]  # FA A: y_t.
    fa_b_transitions_names = fa_b_orig.get_transitions_names()
    b_y_t = [ Int('b_y_%s' % transition) for transition in fa_b_transitions_names ]  # FA B: y_t.
    a_u_q = [ Int('a_u_%s' % state) for state in fa_a_orig.states ]  # FA A: u_q.
    b_u_q = [ Int('b_u_%s' % state) for state in fa_b_orig.states ]  # FA B: u_q.

    # FA A: First conjunct.
    for state in fa_a_orig.states:
        smt.add(Int('a_u_%s' % state) + Sum([Int('a_y_%s' % transition) for transition in fa_a_orig.get_ingoing_transitions_names(state)]) - Sum([Int('a_y_%s' % transition) for transition in fa_a_orig.get_outgoing_transitions_names(state)]) == 0)

    # FA B: First conjunct.
    for state in fa_b_orig.states:
        smt.add(Int('b_u_%s' % state) + Sum([Int('b_y_%s' % transition) for transition in fa_b_orig.get_ingoing_transitions_names(state)]) - Sum([Int('b_y_%s' % transition) for transition in fa_b_orig.get_outgoing_transitions_names(state)]) == 0)

    # FA A: Second conjunct.
    smt.add( And( [ a_y_t[i] >= 0 for i in range( len(fa_a_transitions_names) ) ] ))

    # FA B: Second conjunct.
    smt.add( And( [ b_y_t[i] >= 0 for i in range( len(fa_b_transitions_names) ) ] ))

    # FA A: Third conjunct.
    for symbol in fa_a_orig.alphabet:
        smt.add(Int('hash_%s' % symbol) == Sum([Int('a_y_%s' % transition) for transition in fa_a_orig.get_transitions_names_with_symbol(symbol)]))

    # FA B: Third conjunct.
    for symbol in fa_b_orig.alphabet:
        smt.add(Int('hash_%s' % symbol) == Sum([Int('b_y_%s' % transition) for transition in fa_b_orig.get_transitions_names_with_symbol(symbol)]))

    if reverse_lengths:
        if use_z_constraints:
            #"""
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
            #"""

    # End of SMT formulae initialization.

    # Define additional variables.
    q_checked_pairs = {}
    q_pair_states = deque()

    # Enqueue the initial states.
    for a_initial_state in fa_a_orig.start:
        for b_initial_state in fa_b_orig.start:
            q_pair_states.append([a_initial_state, b_initial_state, False])

    intersect_ab = LFA.get_new()

    fa_a_copy = deepcopy(fa_a_orig)
    fa_b_copy = deepcopy(fa_b_orig)

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

        fa_a_copy.start = {curr_pair[0]}
        fa_b_copy.start = {curr_pair[1]}

        # If the current pair is a single pair created from the previous pair,
        # no need to check for satisfiability.
        #if True:  # Turn Skip feature off.
        if not curr_pair[2]:
            processed_pair_states_cnt += 1

            satisfiable = check_satisfiability(fa_a_copy, fa_b_copy, smt, reverse_lengths, use_z_constraints)
            if satisfiable:
                sat_cnt += 1
        else:
            satisfiable = True
            #printproduct_state_name + " sat", end='  ')
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
                if break_when_final:
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

        #printlen(q_pair_states))

    intersect_ab.remove_useless_transitions()
    intersect_ab.remove_abstract_final_state(abstract_final_symbol, abstract_final_state)
    # Output format: <checked> <processed> <sat> <skipped> <false_cnt> <intersect> <final_cnt>
    print_csv(len(q_checked_pairs))
    print_csv(processed_pair_states_cnt)
    print_csv(sat_cnt)
    print_csv(false_cnt)
    print_csv(skipped_cnt)
    print_csv(len(intersect_ab.states))
    print_csv(len(intersect_ab.final))
    #print(intersect_ab.transitions)
    #intersect_ab.print_automaton()
    #print(intersect_ab.final)


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


def check_satisfiability(fa_a, fa_b, smt, reverse_lengths = True, use_z_constraints = True):
    """
    Check satisfiability for Parikh image using SMT solver Z3.
    :param fa_a: First automaton.
    :param fa_b: Second automaton.
    :return: True if satisfiable; False if not satisfiable.
    """

    #! FIXME what if initial state is also a final state?
    # TMP FIX:
    #if next(iter(fa_a.start)) in fa_a.final:
    #    print("quick true")
    #    return True
    #if next(iter(fa_b.start)) in fa_b.final:
    #    print("quick true")
    #    return True
    if next(iter(fa_a.start)) in fa_a.final and next(iter(fa_b.start)) in fa_b.final:
        #printnext(iter(fa_a.start)) + ',' + next(iter(fa_b.start)) + " final", end='  ')
        #print('final')
        return True

    #smt = Solver()
    smt.push()

    #smt.push()
    # Add clauses – conjunction of formulae.

    # Constraints for 'u_q'.
    for state in fa_a.states:
        if state in fa_a.start:
            smt.add(Int('a_u_%s' % state) == 1)
        elif state in fa_a.final:
            pass
            #smt.add(Or( a_u_q[i] == -1, a_u_q[i] == 0))
            smt.add(Int('a_u_%s' % state) == -1)
        else:
            smt.add(Int('a_u_%s' % state) == 0)

    for state in fa_b.states:
        if state in fa_b.start:
            smt.add(Int('b_u_%s' % state) == 1)
        elif state in fa_b.final:
            pass
            #smt.add(Or( b_u_q[i] == -1, b_u_q[i] == 0))
            smt.add(Int('b_u_%s' % state) == -1)
        else:
            smt.add(Int('b_u_%s' % state) == 0)

    if not reverse_lengths:
        if use_z_constraints:
            #"""
            # FA A: Fourth conjunct.
            for state in fa_a.states:
                if state in fa_a.start:
                    smt.add(Int('a_z_%s' % state) == 1)
                    smt.add(And( [ Int('a_y_%s' % transition) >= 0 for transition in fa_a.get_ingoing_transitions_names(state) ] ))
                else:
                    smt.add(Or(And( And( Int('a_z_%s' % state) == 0 ) , And( [ Int('a_y_%s' % transition) == 0 for transition in fa_a.get_ingoing_transitions_names(state) ] ) ), Or( [ And( Int('a_y_%s' % transition) > 0 , Int('a_z_%s' % transition.split('_')[0]) > 0, Int('a_z_%s' % state) == Int('a_z_%s' % transition.split('_')[0]) + 1) for transition in fa_a.get_ingoing_transitions_names(state) ] )))

            # FA B: Fourth conjunct.
            for state in fa_b.states:
                if state in fa_b.start:
                    smt.add(Int('b_z_%s' % state) == 1)
                    smt.add(And( [ Int('b_y_%s' % transition) >= 0 for transition in fa_b.get_ingoing_transitions_names(state) ] ))
                else:
                    smt.add(Or(And( And( Int('b_z_%s' % state) == 0 ) , And( [ Int('b_y_%s' % transition) == 0 for transition in fa_b.get_ingoing_transitions_names(state) ] ) ), Or( [ And( Int('b_y_%s' % transition) > 0 , Int('b_z_%s' % transition.split('_')[0]) > 0, Int('b_z_%s' % state) == Int('b_z_%s' % transition.split('_')[0]) + 1) for transition in fa_b.get_ingoing_transitions_names(state) ] )))
            #"""

    # Allow multiple final states.
    #FA A: At least one of the final state is reached.
    #smt.add( Or( [ Or( Int('a_u_%s' % state) == -1 , Int('a_u_%s' % state) == 0 ) for state in fa_a.final ] ) )
    #smt.add( Or( [ Int('a_u_%s' % state) == -1 for state in fa_b.final ] ) )
    # FA B: At least one of the final state is reached.
    #smt.add( Or( [ Or( Int('b_u_%s' % state) == -1 , Int('b_u_%s' % state) == 0 ) for state in fa_b.final ] ) )
    #smt.add( Or( [ Int('b_u_%s' % state) == -1 for state in fa_b.final ] ) )

    # Allow multiple inital states.
    # FA A: Choose only one inital state for a run.
    #smt.add( Or( [ And( Int('a_u_%s' % state) == 1, Int('a_z_%s' % state) == 1, And( [ And( Int('a_u_%s' % other_state) == 0, Int('a_z_%s' % other_state) == 0 ) for other_state in fa_a.start if other_state != state ] ) ) for state in fa_a.start ] ) )

    # FA B: Choose only one inital state for a run.
    #smt.add( Or( [ And( Int('b_u_%s' % state) == 1, Int('b_z_%s' % state) == 1, And( [ And( Int('b_u_%s' % other_state) == 0, Int('b_z_%s' % other_state) == 0 ) for other_state in fa_b.start if other_state != state ] ) ) for state in fa_b.start ] ) )

    # Check for satisfiability.
    if smt.check() == sat:
        #printnext(iter(fa_a.start)) + ',' + next(iter(fa_b.start)) + " true", end='  ')
        #print("true", end='  ')
        #print(smt.model())
        smt.pop()
        return True

    smt.pop()
    #printnext(iter(fa_a.start)) + ',' + next(iter(fa_b.start)) + " false", end='  ')
    #print("false")
    return False


def parse_args():
    """Parse arguments using argparse."""
    arg_parser = argparse.ArgumentParser(
        description = 'Construct product (intersection) of two finite automata using abstraction optimization techniques.'
    )
    arg_parser.add_argument('--fa-a-loaded', metavar = 'AUTOMATON_A_LOADED', type = argparse.FileType('rb'),
                    help = 'Automaton A object file to generate product from.')
    arg_parser.add_argument('--fa-b-loaded', metavar = 'AUTOMATON_B_LOADED', type = argparse.FileType('rb'),
                    help = 'Automaton B object file to generate product from.')
    arg_parser.add_argument('--fa-a-path', metavar = 'AUTOMATON_A', type = str,
                    help = 'Automaton A to generate product from.')
    arg_parser.add_argument('--fa-b-path', metavar = 'AUTOMATON_B', type = str,
                    help = 'Automaton B to generate product from.')
    arg_parser.add_argument('--break-when-final', '-b', action = 'store_true',
                    help = 'Break when final state is encountered to execute emptiness test.')
    arg_parser.add_argument('--forward-lengths', '-f', action = 'store_true',
                    help = "Compute forward lengths 'z' for Parikh image.")
    arg_parser.add_argument('--no-z-constraints', '-z', action = 'store_true',
                    help = 'Compute formulae without constraints for connectivity of automaton.')

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

    return fa_a_orig, fa_b_orig, args.break_when_final, not args.forward_lengths, not args.no_z_constraints


if __name__ == "__main__":
    main()

# End of file.
