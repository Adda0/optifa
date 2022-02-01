#!/usr/bin/env python3

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
