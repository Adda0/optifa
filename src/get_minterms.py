#!/usr/bin/env python3

# ====================================================
# file name: get_minterms.py
#
# Script to getminterms from two finite automata.
# ====================================================
# project: Abstraction of State Languages in Automata Algorithms
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
import optifa
from optifa import ProgramConfig, ProgramArgumentsParser


def main():
    """Main script function."""
    config = ProgramArgumentsParser.get_config(ProgramConfig)  # Parse program arguments.

    # Fill Set of sets of symbols between two states with a transition.
    transition_sets_set = set()
    fa_a_sets = config.fa_a_orig.get_transition_sets()
    fa_b_sets = config.fa_b_orig.get_transition_sets()
    print(len(fa_a_sets))
    print(len(fa_b_sets))
    print(fa_a_sets)
    complete_set = set()
    complete_set.update(fa_a_sets)
    complete_set.update(fa_b_sets)
    print(len(complete_set))


    for set in complete_set:







    # Store minterms.
    if config.store_result:
        config.store_result()


class MintermTreeNode:
    """
    Class representing minterm tree node as a binary tree node.
    """

    def __init__(self, new_set, parent = None):
        self.intersect = new_set
        self.left = None
        self.right = None
        self.parent = parent

    def refine_leaf(self, new_set, not_new_set):
        if not self.intersect.isdisjoint(new_set):
            self.insert_left(self.intersect.intersection(new_set))

        if not self.intersect.isdisjoint(not_new_set):
            self.insert_right(self.intersect.intersection(not_new_set))

    def insert_left(self, new_set):
        self.left = MintermTreeNode(new_set, self)

    def insert_right(self, new_set):
        self.right = MintermTreeNode(new_set, self)

class MintermTree:
    """
    Class representing minterm tree structure.
    """

    def __init__(self, alphabet, transitions_set):
        self.leaves = []
        self.alphabet = alphabet
        self.left = None
        self.right = None


    @classmethod
    def get_minterm_tree(cls, alphabet, transitions_set):
        minterm_tree = cls(alphabet, transitions_set)
        for transition_set in transitions_set:
            minterm_tree.refine(transition_set)

        return minterm_tree

    def refine(self, new_set):
        new_leaves = []
        not_new_set = self.alphabet.difference(new_set)

        for leaf in self.leaves:
            new_leaves.append(leaf.refine_leaf(new_set, not_new_set))

        self.leaves = new_leaves


if __name__ == "__main__":
    main()

# End of file.
