#!/usr/bin/env python3

# ====================================================
# file name: optifa.py
#
# Optimizing Automata Product Construction and Emptiness Test base class.
# ====================================================
# project: Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

#import os
import sys
#import symboliclib
#from lfa import LFA
#from collections import deque
#from copy import deepcopy
#import itertools
#import argparse


def print_csv(message):
    """
    Print message in a comma separated values format.
    :param message: Message to be printed.
    """
    print(message, end=',')

class Optifa_a:
    """Optimizing Automata Product Construction and Emptiness Test base class"""

    @staticmethod
    def print_error(message, err_code=1):
        """
        Print error message and end the program.
        :param message: Error message to be printed.
        :param err_code: Error code to end the program with.
        """
        print('ERROR: ' + __file__ + ': ' + message, file=sys.stderr)
        sys.exit(err_code)
# End of file.
