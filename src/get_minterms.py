#!/usr/bin/env python3

# file name: get_minterms.py
#
# Script to get minterms from two finite automata.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

from optifa.basic import ProgramConfig, ProgramArgumentsParser


def main():
    """Main script function."""
    config = ProgramArgumentsParser.get_config(ProgramConfig)  # Parse program arguments.

    print("Number of states:")
    print(len(config.fa_a_orig.states))
    print(len(config.fa_b_orig.states))

    print("Number of used transition symbols:")
    used_alphabet = config.fa_a_orig.get_used_alphabet(config.fa_b_orig)
    used_alphabet_len = len(used_alphabet)
    print(used_alphabet_len)

    # Fill Set of sets of symbols between two states with a transition.
    fa_a_sets = config.fa_a_orig.get_transition_sets()
    fa_b_sets = config.fa_b_orig.get_transition_sets()
    print(len(fa_a_sets))
    print(len(fa_b_sets))
    #print(fa_a_sets)
    #print(fa_b_sets)
    transitions_set = set()
    transitions_set.update(fa_a_sets)
    transitions_set.update(fa_b_sets)
    print(f"All transition sets: {len(transitions_set)}")

    alphabet = config.fa_a_orig.get_used_alphabet().union(config.fa_b_orig.get_used_alphabet())

    minterm_tree = MintermTree.compute_minterm_tree(alphabet, transitions_set)
    final_minterms_len = len(minterm_tree.leaves)
    print(f"Final minterms: {final_minterms_len}")
    print(minterm_tree)

    # Store minterms.
    if config.store_result:
        config.store_result()

    # Replace transition symbols with generated minterms.
    print("Mapping minterms to transition symbols:")
    for transition_set in transitions_set:
        print(f"{transition_set}: ", end="")

        for minterm in minterm_tree.leaves:
            if minterm.intersect.issubset(transition_set):
                print(f"{minterm.intersect},", end="")

        print()

    print(f"Minterm optimization results: {used_alphabet_len} –> {final_minterms_len} => "
          f"{used_alphabet_len - final_minterms_len}")


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
        """
        Get minterms as a tree from given transitions.

        Parameters:
            alphabet (set): Set of automata alphabet.
            transitions_set (set): Set of automata transitions.

        Returns:
            MintermTree: Tree of minterms.
        """
        minterm_tree = cls(alphabet, transitions_set)
        for transition_set in transitions_set:
            minterm_tree.refine(transition_set)

        return minterm_tree

    def refine(self, new_set):
        """
        Refine the entire tree with the given transition set.

        Parameters:
            new_set (set): Transition set to refine the tree with.
        """
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
