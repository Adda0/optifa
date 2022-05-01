#!/usr/bin/env python3

# file name: basic.py
#
# Optimizing Automata Product Construction and Emptiness Test base class.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

from pathlib import Path
import sys
from collections import deque
import itertools
import math

import z3

import symboliclib


def print_csv(message):
    """
    Print message in a comma separated values format.
    :param message: Message to be printed.
    """
    print(message, end=',')


def print_error(message, err_code=1):
    """
    Print error message and end the program.
    :param message: Error message to be printed.
    :param err_code: Error code to end the program with.
    """
    print(Path(__file__).name + ": error: " + message, file=sys.stderr)
    sys.exit(err_code)


def make_pairs(fa_a_orig, fa_b_orig, q_pair_states, q_checked_pairs, intersect, curr_state, single_pair=False):
    a_state = curr_state[0]
    b_state = curr_state[1]
    product_state_name = a_state + ',' + b_state

    new_pairs = deque()
    new_pairs_cnt = 0

    if a_state in fa_a_orig.transitions and b_state in fa_b_orig.transitions:
        for label in fa_a_orig.transitions[a_state]:
            if label in fa_b_orig.transitions[b_state]:
                endstates = itertools.product(fa_a_orig.transitions[a_state][label],
                                              fa_b_orig.transitions[b_state][label])
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
    """
    Add persistent formulae valid for every product state.

    Parameters:
        smt (smt.Solver): Smt solver to solve Parikh image satisfiability.
        fa_a_orig (symboliclib.LFA): First finite automaton.
        fa_b_orig (symboliclib.LFA): Second finite automaton.
        config (optifa.ProgramConfig): Configuration of Parikh image computation.
    """

    # FA A: First conjunct.
    for state in fa_a_orig.states:
        smt.add(z3.Int('a_u_%s' % state) + z3.Sum(
            [z3.Int('a_y_%s' % transition) for transition in fa_a_orig.get_ingoing_transitions_names(state)]) - z3.Sum(
            [z3.Int('a_y_%s' % transition) for transition in fa_a_orig.get_outgoing_transitions_names(state)]) == 0)

    # FA B: First conjunct.
    for state in fa_b_orig.states:
        smt.add(z3.Int('b_u_%s' % state) + z3.Sum(
            [z3.Int('b_y_%s' % transition) for transition in fa_b_orig.get_ingoing_transitions_names(state)]) - z3.Sum(
            [z3.Int('b_y_%s' % transition) for transition in fa_b_orig.get_outgoing_transitions_names(state)]) == 0)

    # FA A: Second conjunct.
    smt.add(z3.And([z3.Int('a_y_%s' % transition) >= 0 for transition in fa_a_orig.get_transitions_names()]))

    # FA B: Second conjunct.
    smt.add(z3.And([z3.Int('b_y_%s' % transition) >= 0 for transition in fa_b_orig.get_transitions_names()]))

    # FA A: Third conjunct.
    for symbol in fa_a_orig.alphabet:
        smt.add(z3.Int('hash_%s' % symbol) == z3.Sum(
            [z3.Int('a_y_%s' % transition) for transition in fa_a_orig.get_transitions_names_with_symbol(symbol)]))

    # FA B: Third conjunct.
    for symbol in fa_b_orig.alphabet:
        smt.add(z3.Int('hash_%s' % symbol) == z3.Sum(
            [z3.Int('b_y_%s' % transition) for transition in fa_b_orig.get_transitions_names_with_symbol(symbol)]))

    if config.reverse_lengths:
        if config.use_z_constraints:
            # FA A: Fourth conjunct.
            for state in fa_a_orig.states:
                if state in fa_a_orig.final:
                    smt.add(z3.Int('a_z_%s' % state) == 1)
                    smt.add(z3.And([z3.Int('a_y_%s' % transition) >= 0 for transition in
                                 fa_a_orig.get_outgoing_transitions_names(state)]))

                if state not in fa_a_orig.start and state not in fa_a_orig.final:
                    smt.add(z3.Or(z3.And(z3.And(z3.Int('a_z_%s' % state) == 0),
                                  z3.And([z3.Int('a_y_%s' % transition) == 0
                                  for transition in fa_a_orig.get_ingoing_transitions_names(state)])),
                                  z3.Or([z3.And(z3.Int('a_y_%s' % transition) >= 0,
                                  z3.Int('a_z_%s' % transition.split('_')[0]) > 0,
                                  z3.Int('a_z_%s' % state) == z3.Int('a_z_%s' % transition.split('_')[0]) - 1)
                                  for transition in fa_a_orig.get_ingoing_transitions_names(state)])))

            # FA B: Fourth conjunct.
            for state in fa_b_orig.states:
                if state in fa_b_orig.final:
                    smt.add(z3.Int('b_z_%s' % state) == 1)
                    smt.add(z3.And([z3.Int('b_y_%s' % transition) >= 0 for transition in
                                 fa_b_orig.get_outgoing_transitions_names(state)]))

                if state not in fa_b_orig.start and state not in fa_a_orig.final:
                    smt.add(z3.Or(z3.And(z3.And(z3.Int('b_z_%s' % state) == 0),
                            z3.And([z3.Int('b_y_%s' % transition) == 0
                            for transition in fa_b_orig.get_ingoing_transitions_names(state)])),
                            z3.Or([z3.And(z3.Int('b_y_%s' % transition) >= 0,
                            z3.Int('b_z_%s' % transition.split('_')[0]) > 0,
                            z3.Int('b_z_%s' % state) == z3.Int('b_z_%s' % transition.split('_')[0]) - 1)
                            for transition in fa_b_orig.get_ingoing_transitions_names(state)])))

    # End of SMT formulae initialization.


def add_state_specific_formulae(smt, fa_a, fa_b, config):
    """
    Add formulae specific for the current states (initial, final and the rest) in the original automata.
    """
    # Constraints for 'u_q'.
    for state in fa_a.states:
        if state in fa_a.start:
            smt.add(z3.Int('a_u_%s' % state) == 1)
        elif state in fa_a.final:
            # smt.add(z3.Or( a_u_q[i] == -1, a_u_q[i] == 0))
            smt.add(z3.Int('a_u_%s' % state) == -1)
        else:
            smt.add(z3.Int('a_u_%s' % state) == 0)

    for state in fa_b.states:
        if state in fa_b.start:
            smt.add(z3.Int('b_u_%s' % state) == 1)
        elif state in fa_b.final:
            # smt.add(z3.Or( b_u_q[i] == -1, b_u_q[i] == 0))
            smt.add(z3.Int('b_u_%s' % state) == -1)
        else:
            smt.add(z3.Int('b_u_%s' % state) == 0)

    if not config.reverse_lengths:
        if config.use_z_constraints:
            # FA A: Fourth conjunct.
            for state in fa_a.states:
                if state in fa_a.start:
                    smt.add(z3.Int('a_z_%s' % state) == 1)
                    smt.add(z3.And([z3.Int('a_y_%s' % transition) >= 0
                            for transition in fa_a.get_ingoing_transitions_names(state)]))
                else:
                    smt.add(z3.Or(z3.And(z3.And(z3.Int('a_z_%s' % state) == 0),
                            z3.And([z3.Int('a_y_%s' % transition) == 0
                            for transition in fa_a.get_ingoing_transitions_names(state)])),
                            z3.Or([z3.And(z3.Int('a_y_%s' % transition) > 0,
                            z3.Int('a_z_%s' % transition.split('_')[0]) > 0,
                            z3.Int('a_z_%s' % state) == z3.Int('a_z_%s' % transition.split('_')[0]) + 1)
                            for transition in fa_a.get_ingoing_transitions_names(state)])))

            # FA B: Fourth conjunct.
            for state in fa_b.states:
                if state in fa_b.start:
                    smt.add(z3.Int('b_z_%s' % state) == 1)
                    smt.add(z3.And([z3.Int('b_y_%s' % transition) >= 0 for transition in
                                 fa_b.get_ingoing_transitions_names(state)]))
                else:
                    smt.add(z3.Or(z3.And(z3.And(z3.Int('b_z_%s' % state) == 0),
                            z3.And([z3.Int('b_y_%s' % transition) == 0
                            for transition in fa_b.get_ingoing_transitions_names(state)])),
                            z3.Or([z3.And(z3.Int('b_y_%s' % transition) > 0,
                            z3.Int('b_z_%s' % transition.split('_')[0]) > 0,
                            z3.Int('b_z_%s' % state) == z3.Int('b_z_%s' % transition.split('_')[0]) + 1)
                            for transition in fa_b.get_ingoing_transitions_names(state)])))

    # Allow multiple final states.
    # FA A: At least one of the final state is reached.
    # smt.add( z3.Or( [ z3.Or( z3.Int('a_u_%s' % state) == -1 , z3.Int('a_u_%s' % state) == 0 ) for state in fa_a.final ] ) )
    # smt.add( z3.Or( [ z3.Int('a_u_%s' % state) == -1 for state in fa_b.final ] ) )
    # FA B: At least one of the final state is reached.
    # smt.add( z3.Or( [ z3.Or( z3.Int('b_u_%s' % state) == -1 , z3.Int('b_u_%s' % state) == 0 ) for state in fa_b.final ] ) )
    # smt.add( z3.Or( [ z3.Int('b_u_%s' % state) == -1 for state in fa_b.final ] ) )

    # Allow multiple inital states.
    # FA A: Choose only one inital state for a run.
    # smt.add( z3.Or( [ z3.And( z3.Int('a_u_%s' % state) == 1, z3.Int('a_z_%s' % state) == 1, z3.And( [ z3.And( z3.Int('a_u_%s' % other_state) == 0, z3.Int('a_z_%s' % other_state) == 0 ) for other_state in fa_a.start if other_state != state ] ) ) for state in fa_a.start ] ) )

    # FA B: Choose only one inital state for a run.
    # smt.add( z3.Or( [ z3.And( z3.Int('b_u_%s' % state) == 1, z3.Int('b_z_%s' % state) == 1, z3.And( [ z3.And( z3.Int('b_u_%s' % other_state) == 0, z3.Int('b_z_%s' % other_state) == 0 ) for other_state in fa_b.start if other_state != state ] ) ) for state in fa_b.start ] ) )


def check_length_satisfiability(config, fa_a_formulae_dict, fa_b_formulae_dict):
    """
    Check satisfiability for length abstraction formulae using SMT solver Z3.
    :param fa_a_formulae_dict: Dictionary with formulae for FA A.
    :param fa_b_formulae_dict: Dictionary with formulae for FA B.
    :return: True if satisfiable; False if not satisfiable.
    """
    if not config.smt_free:
        smt = z3.Solver()
        fa_a_var = z3.Int('fa_a_var')
        fa_b_var = z3.Int('fa_b_var')
        smt.add(fa_a_var >= 0, fa_b_var >= 0)

    # Check for every formulae combination.
    for fa_a_id in get_only_formulae(fa_a_formulae_dict):
        for fa_b_id in get_only_formulae(fa_b_formulae_dict):
            if config.smt_free:  # Without using SMT solver.
                # Handle legths are equal, True without the need to resolve loops.
                if fa_a_id[0] == fa_b_id[0]:
                    return True

                # Handle lengths are distinct, further checking needed.
                elif fa_a_id[0] > fa_b_id[0]:  # FA A handle is longer.
                    if solve_for_one_handle_longer(fa_a_id, fa_b_id):
                        return True

                else:  # FA B handle is longer.
                    if solve_for_one_handle_longer(fa_b_id, fa_a_id):
                        return True

            else:  # Using SMT solver.
                smt.push()
                smt.add(fa_a_id[0] + fa_a_id[1] * fa_a_var == fa_b_id[0] + fa_b_id[1] * fa_b_var)

                if smt.check() != z3.unsat:
                    return True

                smt.pop()

    return False


def check_single_length_satisfiability(config, fa_a_formula, fa_b_formula):
    """
    Check satisfiability for length abstraction formulae using SMT solver Z3.
    :param fa_a_formulae_dict: Dictionary with formulae for FA A.
    :param fa_b_formulae_dict: Dictionary with formulae for FA B.
    :return: True if satisfiable; False if not satisfiable.
    """
    if not config.smt_free:
        smt = z3.Solver()
        fa_a_var = z3.Int('fa_a_var')
        fa_b_var = z3.Int('fa_b_var')
        smt.add(fa_a_var >= 0, fa_b_var >= 0)

    # Check for every formulae combination.
    if config.smt_free:  # Without using SMT solver.
        # Handle legths are equal, True without the need to resolve loops.
        if fa_a_formula[0] == fa_b_formula[0]:
            return True

        # Handle lengths are distinct, further checking needed.
        elif fa_a_formula[0] > fa_b_formula[0]:  # FA A handle is longer.
            if solve_for_one_handle_longer(fa_a_formula, fa_b_formula):
                return True

        else:  # FA B handle is longer.
            if solve_for_one_handle_longer(fa_b_id, fa_b_formula):
                return True

    else:  # Using SMT solver.
        smt.push()
        smt.add(fa_a_formula[0] + fa_a_formula[1] * fa_a_var == fa_b_formula[0] + fa_b_formula[1] * fa_b_var)

        if smt.check() != z3.unsat:
            return True

        smt.pop()

    return False


def get_only_formulae(formulae_dict):
    only_formulae = []
    for accept_state in formulae_dict:
        try:
            only_formulae.append([formulae_dict[accept_state][1], formulae_dict[accept_state][2]])
        except IndexError:
            only_formulae.append([formulae_dict[accept_state][1]])

    return only_formulae


def solve_for_one_handle_longer(fa_a_id, fa_b_id):
    fa_a_id[0] -= fa_b_id[0]
    fa_b_id[0] = 0

    if fa_a_id[1] == 0 and fa_b_id[1] == 0:  # No loops.
        return False

    elif fa_b_id[1] == 0:
        return False

    elif fa_a_id[1] == 0:
        curr_num = 0
        while curr_num <= fa_a_id[0]:
            if curr_num == fa_a_id[0]:
                return True
            else:
                curr_num += fa_b_id[1]
        return False

    else:  # Two loops:
        gcd = math.gcd(fa_a_id[1], fa_b_id[1])
        if gcd == 1:
            return True
        else:
            y = - fa_a_id[0]
            while y < gcd:
                y += fa_a_id[1]
            if y % gcd == 0:
                return True
            else:
                return False

# End of file.
