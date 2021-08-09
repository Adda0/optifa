#!/usr/bin/env python3

# ====================================================
# file name: resolve_satisfiability.py
#
# Script to resolve satisfiable of given formulae using Z3 SMT solver.
# ====================================================
# project: IP1 | Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

import os
import sys
import symboliclib
from lfa import LFA
from z3 import *
from collections import deque
from copy import deepcopy
import itertools

# Main script function.
def main():
    fa_a_name = sys.argv[1]
    fa_b_name = sys.argv[2]

    fa_a_orig = symboliclib.parse(fa_a_name)
    fa_b_orig = symboliclib.parse(fa_b_name)
    A_larger = True

    # Print sizes of original automata.
    if len(fa_a_orig.states) > len(fa_b_orig.states):
        print(len(fa_a_orig.states), end=' ')
        print(len(fa_b_orig.states), end=' ')
    else:
        A_larger = False
        print(len(fa_b_orig.states), end=' ')
        print(len(fa_a_orig.states), end=' ')

    # Run twice – once for emptiness test (break_when_final == True) and
    # once for full product construction (break_when_final == False).
    for break_when_final in [True, False]:
        #print(len(fa_a_orig.states) * len(fa_b_orig.states), end=' ')

        q_a_states = deque()
        q_b_states = deque()

        processed_pair_states_cnt = 0

        q_checked_pairs = {}
        q_pair_states = deque()

        # Enqueue the initial states.
        for a_initial_state in fa_a_orig.start:
            for b_initial_state in fa_b_orig.start:
                q_pair_states.append([a_initial_state, b_initial_state, False])


        # Generate signle handle and loop automata per original input automaton.
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

            q_checked_pairs[curr_pair[0] + ',' + curr_pair[1]] = True
            # DEBUG:
            #if curr_pair[0]:
            #    print('Skip: ' + str(curr_pair))
            #else:
            #    print(curr_pair)

            fa_a_unified.start = {curr_pair[0]}
            fa_b_unified.start = {curr_pair[1]}

            # If the current pair is a single pair created from the previous pair,
            # no need to check for satisfiability.
            #if True:  # Turn Skip feature off.
            if not curr_pair[2]:
                processed_pair_states_cnt += 1
                fa_a_unified.determinize_check(fa_a_handle_and_loop)
                fa_b_unified.determinize_check(fa_b_handle_and_loop)

                if not fa_a_handle_and_loop.final or not fa_b_handle_and_loop.final:
                    break

                fa_a_formulae_dict = fa_a_handle_and_loop.count_formulae_for_lfa()
                #print(fa_a_formulae_dict)  # DEBUG
                fa_b_formulae_dict = fa_b_handle_and_loop.count_formulae_for_lfa()
                #print(fa_b_formulae_dict)  # DEBUG

                satisfiable = check_satisfiability(fa_a_formulae_dict, fa_b_formulae_dict)
                #print(satisfiable)
                if satisfiable:
                    sat_cnt += 1
            else:
                satisfiable = True
                skipped_cnt += 1

            if satisfiable:
                intersect_ab.states.add(curr_pair[0] + ',' + curr_pair[1])
                #print(len(intersect_ab.states))  # Debug

                if curr_pair[0] in fa_a_orig.final and curr_pair[1] in fa_b_orig.final:
                    # Automata have a non-empty intersection. We can end the testing here as we have found a solution.
                    # Output format: 'T <checked> <processed> <sat> <skipped> <false_cnt>
                    #fa_a_handle_and_loop.print_automaton()
                    #fa_b_handle_and_loop.print_automaton()
                    intersect_ab.final.add(curr_pair[0] + ',' + curr_pair[1])
                    """
                    print('')
                    print('T', end = ' ')
                    print(len(q_checked_pairs), end = ' ')
                    print(processed_pair_states_cnt, end = ' ')
                    print(sat_cnt, end=' ')
                    print(false_cnt, end=' ')
                    print(skipped_cnt, end = ' ')
                    print(len(fa_a_handle_and_loop.states), end=' ')
                    print(len(fa_b_handle_and_loop.states), end=' ')
                    print(len(intersect_ab.states),  end=' ')
                    print(len(intersect_ab.final), end=' ')
                    """
                    found = True
                    if break_when_final:
                        break

                #print(q_pair_states)
                old_pair_states_len = len(q_pair_states)
                make_pairs(fa_a_orig, fa_b_orig, q_pair_states, q_checked_pairs, curr_pair)
                pair_states_len_diff = len(q_pair_states) - old_pair_states_len
                #print(pair_states_len_diff)
                #print(q_pair_states)
            else:
                false_cnt += 1

        if not found:
            """
            #print(f"handle and loop a: {len(fa_a_handle_and_loop.states)}")
            #print(f"handle and loop b: {len(fa_b_handle_and_loop.states)}")
            print('')
            # Output format: 'F <checked> <processed> <skipped> <false_cnt>'
            print('F', end = ' ')
            print(len(q_checked_pairs), end = ' ')
            print(processed_pair_states_cnt, end = ' ')
            print(sat_cnt, end=' ')
            print(false_cnt, end=' ')
            print(skipped_cnt, end = ' ')
            print(len(fa_a_handle_and_loop.states), end=' ')
            print(len(fa_b_handle_and_loop.states), end=' ')
            print(len(intersect_ab.states),  end=' ')
            print(len(intersect_ab.final), end=' ')
            #print("FAILURE: Automata have an empty intersection.")
            """

        # Output format: <checked> <processed> <sat> <skipped> <false_cnt> <intersect> <final_cnt>
        print('')
        print('I', end=' ')
        print(len(q_checked_pairs), end = ' ')
        print(processed_pair_states_cnt, end = ' ')
        print(sat_cnt, end=' ')
        print(false_cnt, end=' ')
        print(skipped_cnt, end = ' ')
        if A_larger:
            print(len(fa_a_handle_and_loop.states), end=' ')
            print(len(fa_b_handle_and_loop.states), end=' ')
        else:
            print(len(fa_b_handle_and_loop.states), end=' ')
            print(len(fa_a_handle_and_loop.states), end=' ')
        print(len(intersect_ab.states),  end=' ')
        print(len(intersect_ab.final), end=' ')
        #intersect_ab.print_automaton()
        #print(intersect_ab.final)
        #fa_a_handle_and_loop.print_automaton()
        #fa_b_handle_and_loop.print_automaton()


        #orig_a = symboliclib.parse(fa_a_name)
        #orig_b = symboliclib.parse(fa_b_name)
        orig_a = fa_a_orig
        orig_b = fa_b_orig
        #orig_a.unify_transition_symbols()
        #orig_b.unify_transition_symbols()
        #print(f"A states: {len(orig_a.states)}")
        #print(f"B states: {len(orig_b.states)}")
        intersect = orig_a.intersection_count(orig_b, break_when_final)
        #intersect.print_automaton()
        #print(cnt_operations)
        print('')
        print('N', end=' ')
        print(len(intersect.states), end=' ')
        print(len(intersect.final), end=' ')
        #intersect = intersect.simple_reduce()
        #print(f"Naive intersect simple_reduce: {len(intersect.states)}")
        #print(f"Naive intersect simple_reduce final: {len(intersect.final)}")

        print()
        #print(intersect.final)
        #intersect_ab = intersect_ab.simple_reduce()
        #print(f"Intersect_ab sr: {len(intersect_ab.states)}")
        #print(f"Intersect_ab sr final: {len(intersect_ab.final)}")


def make_pairs(fa_a_orig, fa_b_orig, q_pair_states, q_checked_pairs, curr_state, single_pair = False):
    #if single_pair == None:
    #    single_pair = True if (len(q_a_states) == 1 and len(q_b_states) == 1) else False
    a_state = curr_state[0]
    b_state = curr_state[1]

    new_pairs = deque()
    new_pairs_cnt = 0

    if a_state in fa_a_orig.transitions and b_state in fa_b_orig.transitions:
        for label in fa_a_orig.transitions[a_state]:
            if label in fa_b_orig.transitions[b_state]:
                endstates = itertools.product(fa_a_orig.transitions[a_state][label], fa_b_orig.transitions[b_state][label])
                for endstate in endstates:
                    #endstate_str = endstate[0] + "_1|" + endstate[1] + "_2]"

                    #if label not in intersect.transitions[combined_str]:
                    #    intersect.transitions[combined_str][label] = [endstate_str]
                    #else:
                    #    intersect.transitions[combined_str][label].append(endstate_str)

                    end_str = endstate[0] + ',' + endstate[1]
                    #endstate = [endstate[0], endstate[1]]
                    new_pairs_cnt += 1
                    if end_str not in q_checked_pairs:
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


def check_satisfiability(fa_a, fa_b):
    """
    Check satisfiability for Parikh image using SMT solver Z3.
    :param fa_a: First automaton.
    :param fa_b: Second automaton.
    :return: True if satisfiable; False if not satisfiable.
    """

    smt = Solver()
    # Create lists of variables for conjunction of formulae.
    y_t_a = [ Int('y_a_%s' % i) for i in range( len(fa_a.transitions) ) ]  # FA A: y_t.
    u_q_a = [ Int('u_a_%s' % i) for i in range( len(fa_a.states) ) ]  # FA A: u_q.

    smt.push()
    # Add clauses – conjunction of formulae.

    # Constraints for 'u_q'.
    for i, state in enumerate(fa_a.states):
        if state in fa_a.start:
            smt.add(u_q_a[i] = 1)
        else if state in fa_a.final:
            smt.add(u_q_a[i] = -1)  #? TODO what about 'or u_q_a[i] = -0'?
        else:
            smt.add(u_q_a[i] = 0)

    smt.add()  # FA A: First conjunct.
    smt.add( And( [ y_t_a[i] >= 0 for i in range( len(fa_a.transitions) ) ] ))  # FA A: Second conjunct.
    smt.add()  # FA A: Third conjunct.
    smt.add()  # FA A: Forth conjunct.



    if smt.check() == sat:
        #print(smt.model())  # DEBUG
        return True
    smt.pop()
    return False


if __name__ == "__main__":
    main()

# End of file.
