#!/usr/bin/env python3

# file name: get_minterms.py
#
# Script to get minterms from two finite automata.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

import pickle
import symboliclib

from optifa.program_config import ProgramConfig, ProgramArgumentsParser
from optifa.minterms import MintermTree


def main():
    """Main script function."""
    config = ArgumentsParser.get_config(Config)  # Parse program arguments.

    #print("Number of states:")
    #print(len(config.fa_a_orig.states))
    #print(len(config.fa_b_orig.states))

    used_alphabet = config.fa_a_orig.get_used_alphabet(config.fa_b_orig)
    used_alphabet_len = len(used_alphabet)
    #print("Number of used transition symbols:")
    #print(used_alphabet_len)

    # Fill Set of sets of symbols between two states with a transition.
    fa_a_sets = config.fa_a_orig.get_transition_sets()
    fa_b_sets = config.fa_b_orig.get_transition_sets()
    #print("Number of transition sets:")
    #print(len(fa_a_sets))
    #print(len(fa_b_sets))
    #print(fa_a_sets)
    #print(fa_b_sets)
    transitions_set = set()
    transitions_set.update(fa_a_sets)
    transitions_set.update(fa_b_sets)
    #print(f"All transition sets: {len(transitions_set)}")

    alphabet = config.fa_a_orig.get_used_alphabet().union(config.fa_b_orig.get_used_alphabet())

    minterm_tree = MintermTree.compute_minterm_tree(alphabet, transitions_set)
    final_minterms_len = len(minterm_tree.leaves)
    #print(f"Final minterms: {final_minterms_len}")
    #print(minterm_tree)

    # Replace transition symbols with generated minterms.
    #print("Mapping minterms to transition symbols:")
    for transition_set in transitions_set:
        #print(f"{transition_set}: ", end="")

        for minterm in minterm_tree.leaves:
            if minterm.intersect.issubset(transition_set):
                #print(f"{minterm.intersect},", end="")
                pass

        #print()

    #print(f"Minterm optimization results: {used_alphabet_len} –> {final_minterms_len} => "
    #      f"{used_alphabet_len - final_minterms_len}")

    # Store automata with minterms.
    transitions_list = []
    for transition_set in transitions_set:
        transitions_list.append(list(transition_set))

    config.fa_a_orig.replace_transitions_with_minterms(minterm_tree.leaves, transitions_list)
    config.fa_b_orig.replace_transitions_with_minterms(minterm_tree.leaves, transitions_list)

    # Store minterms.
    if config.result_fa_a:
        pass
        config.fa_a_orig.print_automaton(config.result_fa_a)
    if config.result_fa_b:
        config.fa_b_orig.print_automaton(config.result_fa_b)

    print(f"{used_alphabet_len},{final_minterms_len}")


class ArgumentsParser(ProgramArgumentsParser):
    def __init__(self):
        super().__init__()

        self.arg_parser.description = 'Compute minterms from finite automata.'

        # Define script-specific arguments.
        self.arg_parser.add_argument('--result-fa-a', metavar='RESULT_FILE_FA_A', type=str,
                                     help='Result file to store the generated finite automaton with minterms for FA A.')
        self.arg_parser.add_argument('--result-fa-b', metavar='RESULT_FILE_FA_A', type=str,
                                     help='Result file to store the generated finite automaton with minterms for FA B.')


class Config(ProgramConfig):
    """Class for storing program configurations passed as command line arguments."""

    def __init__(self, args):
        super().__init__(args)

        self.result_fa_a = args.result_fa_a
        self.result_fa_b = args.result_fa_b


if __name__ == "__main__":
    main()

# End of file.
