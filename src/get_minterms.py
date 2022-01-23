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
    transitions_set = set()
    transitions_set.update(fa_a_sets)
    transitions_set.update(fa_b_sets)
    print(len(transitions_set))

    alphabet = config.fa_a_orig.alphabet.union(config.fa_b_orig.alphabet)

    minterm_tree = MintermTree.compute_minterm_tree(alphabet, transitions_set)
    print(minterm_tree)

    # Store minterms.
    if config.store_result:
        config.store_result()


class MintermTreeNode:
    """
    Class representing minterm tree node as a binary tree node.
    """

    def __init__(self, new_set, parent = None):
        self.intersect = new_set
        #print(f"Node intersect: {self.intersect}")
        self.left = None
        self.right = None
        self.parent = parent

    def refine_leaf(self, new_set, not_new_set):
        """
        Recursively refine leaf subtree.
        """
        leaves = []
        if not self.intersect.isdisjoint(new_set):
            leaves.append(self.insert_left(self.intersect.intersection(new_set)))

        if not self.intersect.isdisjoint(not_new_set):
            leaves.append(self.insert_right(self.intersect.intersection(not_new_set)))

        return leaves

    def insert_left(self, new_set):
        """
        Insert to the left subtree.
        """
        self.left = MintermTreeNode(new_set, self)
        return self.left

    def insert_right(self, new_set):
        """
        Insert to the right subtree.
        """
        self.right = MintermTreeNode(new_set, self)
        return self.right

    def __repr__(self):
        return f"{self.intersect}"


class MintermTree:
    """
    Class representing minterm tree structure.
    """

    def __init__(self, alphabet, transitions_set):
        self.alphabet = alphabet
        self.transitions_set = transitions_set
        self.root = MintermTreeNode(alphabet)
        self.leaves = [self.root]

    @classmethod
    def compute_minterm_tree(cls, alphabet, transitions_set):
        minterm_tree = cls(alphabet, transitions_set)
        for transition_set in transitions_set:
            minterm_tree.refine(transition_set)

        return minterm_tree

    def refine(self, new_set):
        new_leaves = []
        not_new_set = self.alphabet.difference(new_set)

        for leaf in self.leaves:
            new_leaves.extend(leaf.refine_leaf(new_set, not_new_set))

        self.leaves = new_leaves

        #for leaf in self.leaves:
        #   print(leaf.intersect)

    def __repr__(self):
        """
        Print Minterms in a tree.
        """
        for leaf in self.leaves:
            print(leaf)

        return ""


if __name__ == "__main__":
    main()

# End of file.
