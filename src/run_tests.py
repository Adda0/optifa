#!/usr/bin/env -S python3 -u

# file name: run_tests.py
#
# Script to run tests.
#
# project: Abstraction of State Languages in Automata Algorithms
#
# author: David Chocholatý (xchoch08), FIT BUT

import sys
from copy import deepcopy
import itertools
import argparse
from dataclasses import dataclass
import math

import z3
from z3 import And, Int, Or, Sum

import symboliclib
from lfa import LFA
from optifa import *

import os
from pathlib import Path
import random

import subprocess

import resolve_satisfiability_combined
import resolve_satisfiability_length_abstraction
import resolve_satisfiability_parikh_image


# Main script function.
def main():
    config = ArgumentParser.get_config(Config)  # Parse program arguments.
    if config.root_dir:
        root_dir = Path(config.root_dir)

        directories = [x for x in root_dir.iterdir() if x.is_dir()]
        random.shuffle(directories)
        for dir in directories:
            print(f"Category: {dir}")
            execute_tests(config, dir)
        else:
            print(f"Category: {root_dir}")
            execute_tests(config, root_dir)
    elif config.single:
        print(f"Single test:")
        execute_tests(config)


def load_automata(first_automaton, second_automaton, first_loaded, second_loaded):
    out = subprocess.Popen(
        ["python3",
         "load_automata.py",
         "-a",
         f"{first_automaton}",
         "-b",
         f"{second_automaton}",
         "--out_a",
         f"{first_loaded}",
         "--out_b",
         f"{second_loaded}",
         ],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )


def skip_pi(csv_data_file):
    with open(csv_data_file, "a") as data_file:
        data_file.write(",,,,,,,,,,,,,,")


def print_automata_sizes(first_automaton, second_automaton, csv_data_file):
    out = subprocess.Popen(
        ["python3",
         "print_automata_sizes.py",
         f"{first_automaton}",
         f"{second_automaton}",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    out.wait()

    with open(csv_data_file, "a") as data_file:
        data_file.write(out.communicate()[0].decode("utf-8"))


def execute_tests(config, directory=None):
    timeout = 10 * 60
    # timeout = 0.0001

    csv_data_file = config.store_result
    tmp_product_data_file = "tmp_product_data_file"
    csv_time_data_file = "time_csv"
    first_loaded = "fa_a_loaded"
    second_loaded = "fa_b_loaded"

    length_abstraction = "length_abstraction"
    pi_abstraction = "parikh_image"
    combined_abstraction = "combined"

    if config.single:
        run_single_experiment(combined_abstraction, csv_data_file, csv_time_data_file, config.first_automaton,
                              first_loaded, length_abstraction, pi_abstraction, config.second_automaton, second_loaded,
                              timeout, tmp_product_data_file)
    else:
        files = [x for x in directory.iterdir() if x.is_file()]
        if files:
            for _ in range(config.num_experiments):
                first_automaton = random.choice(files)
                second_automaton = random.choice(list(filter(lambda file: file != first_automaton, files)))
                run_single_experiment(combined_abstraction, csv_data_file, csv_time_data_file, first_automaton,
                                      first_loaded, length_abstraction, pi_abstraction, second_automaton, second_loaded,
                                      timeout, tmp_product_data_file)


def run_single_experiment(combined_abstraction, csv_data_file, csv_time_data_file, first_automaton, first_loaded,
                          length_abstraction, pi_abstraction, second_automaton, second_loaded, timeout,
                          tmp_product_data_file):
    print(f"Experiment: {first_automaton}, {second_automaton}")
    start_experiment(csv_data_file)
    load_automata(first_automaton, second_automaton, first_loaded, second_loaded)
    with open(csv_data_file, "a") as data_file:
        data_file.write(f"{first_automaton},{second_automaton},")
    print_automata_sizes(first_automaton, second_automaton, csv_data_file)
    generate_basic_product(["--break-when-final"], csv_time_data_file, first_loaded, second_loaded,
                           tmp_product_data_file, csv_data_file, timeout)
    run_experiment(length_abstraction, ["--smt", "--break-when-final"], csv_time_data_file, first_loaded,
                   second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)
    run_experiment(length_abstraction, ["--break-when-final"], csv_time_data_file, first_loaded, second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)
    skip_pi(csv_data_file)
    skip_pi(csv_data_file)
    run_experiment(pi_abstraction, ["--no-z-constraints", "--break-when-final", "--timeout", "600"], csv_time_data_file,
                   first_loaded,
                   second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)
    run_experiment(combined_abstraction, ["--no-z-constraints", "--break-when-final", "--timeout", "600"],
                   csv_time_data_file,
                   first_loaded, second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)
    generate_basic_product([], csv_time_data_file, first_loaded, second_loaded,
                           tmp_product_data_file, csv_data_file, timeout)
    run_experiment(length_abstraction, ["--smt"], csv_time_data_file, first_loaded, second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)
    run_experiment(length_abstraction, [], csv_time_data_file, first_loaded, second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)
    skip_pi(csv_data_file)
    skip_pi(csv_data_file)
    run_experiment(pi_abstraction, ["--no-z-constraints", "--timeout", "600"], csv_time_data_file, first_loaded,
                   second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)
    run_experiment(combined_abstraction, ["--no-z-constraints", "--timeout", "600"], csv_time_data_file, first_loaded,
                   second_loaded,
                   tmp_product_data_file, csv_data_file, timeout)


def generate_basic_product(flags, csv_time_data_file, first_automaton, second_automaton, tmp_product_data_file,
                           csv_data_file, timeout):
    flags = ' '.join(flags)
    out = subprocess.Popen(
        ["hyperfine",
         f"python3 generate_basic_product.py --loaded {flags} --fa-a {first_automaton} "
         f"--fa-b {second_automaton} > {tmp_product_data_file}",
         "--export-csv",
         f"{csv_time_data_file}",
         "-u",
         "second",
         "-r",
         "2"
         ],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    process_experiment_result("basic", csv_data_file, csv_time_data_file, out, timeout, tmp_product_data_file)


def run_experiment(abstraction, flags, csv_time_data_file, first_automaton, second_automaton, tmp_product_data_file,
                   csv_data_file, timeout):
    flags = ' '.join(flags)
    out = subprocess.Popen(
        ["hyperfine",
         f"python3 resolve_satisfiability_{abstraction}.py --loaded {flags} --fa-a {first_automaton} "
         f"--fa-b {second_automaton} > {tmp_product_data_file}",
         "--export-csv",
         f"{csv_time_data_file}",
         "-u",
         "second",
         "-r",
         "2"
         ],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    process_experiment_result(abstraction, csv_data_file, csv_time_data_file, out, timeout, tmp_product_data_file)


def start_experiment(csv_data_file):
    with open(csv_data_file, "a") as data_file:
        data_file.write("\n")


def process_experiment_result(abstraction, csv_data_file, csv_time_data_file, out, timeout, tmp_product_data_file):
    length_abstraction = "length_abstraction"
    pi_abstraction = "parikh_image"
    combined_abstraction = "combined"

    try:
        out.wait(timeout)
    except subprocess.TimeoutExpired:
        out.kill()
        with open(csv_data_file, "a") as data_file:
            if abstraction == "basic":
                data_file.write(",,,,,,,,,")
            elif abstraction == length_abstraction:
                data_file.write(",,,,,,,,,,,,,,,,")
            elif abstraction == pi_abstraction:
                data_file.write(",,,,,,,,,,,,,,")
            elif abstraction == combined_abstraction:
                data_file.write(",,,,,,,,,,,,,,,,,,,,")

    else:
        # print(out.returncode)
        if not out.returncode:
            with open(csv_data_file, "a") as data_file:
                with open(tmp_product_data_file, "r") as product_data_file:
                    data_file.write(product_data_file.readline().strip("\n"))

                with open(csv_time_data_file, "r") as time_data_file:
                    # print(time_data_file.readlines())
                    time_data = time_data_file.readlines()[1].strip("\n")
                    # print(time_data)
                    time_data = time_data[time_data.find(','):][1:]
                    data_file.write(f"{time_data},")
        else:
            with open(csv_data_file, "a") as data_file:
                data_file.write(",,,,,,,,,,,,,,")


class Config:
    """Class for storing program configurations passed as command line arguments."""

    def __init__(self, args):

        self.single = args.single
        self.root_dir = args.root_dir

        if args.single:
            self.first_automaton = args.fa_a
            self.second_automaton = args.fa_b
        elif args.root_dir:
            pass
        else:
            raise ValueError("missing finite automata arguments to run tests on")

        self.store_result = args.store_result
        self.num_experiments = args.num_experiments


class ArgumentParser:
    """Class parsing arguments using argparse."""

    def __init__(self):
        self.arg_parser = argparse.ArgumentParser(description='Run tests for state language abstractions.')


        test_type_group = self.arg_parser.add_mutually_exclusive_group(required=True)
        test_type_group.add_argument('--root-dir', '-r', metavar='ROOT_DIRECTORY', type=str,
                                     help='Look for files in the directory and its subdirectories.')
        test_type_group.add_argument('--single', '-s', action='store_true',
                                     help='Run test for a single combination of finite automata.')

        automata_path_group = self.arg_parser.add_argument_group(title="Automata to run tests on",
                                                                 description="The automata paths for automata to "
                                                                             "generate product from.")
        automata_path_group.add_argument('--fa-a', '-a', metavar='AUTOMATON_A', type=str,
                                         help='Automaton A to generate product from.')
        automata_path_group.add_argument('--fa-b', '-b', metavar='AUTOMATON_B', type=str,
                                         help='Automaton B to generate product from.')

        self.arg_parser.add_argument('--num-experiments', '-n', type=int, default=1,
                                     help='Number of experiments to run for each category.')
        self.arg_parser.add_argument('--store-result', '-o', metavar='RESULT_FILE', type=str, required=True,
                                     help='Append results to file RESULT_FILE.')

    def test_for_help(self):
        """Test for '--help' argument and print argparse help message when present."""
        if '--help' in sys.argv or '-h' in sys.argv:
            self.arg_parser.print_help()
            sys.exit(0)

    def parse_args(self):
        """Parse program command line arguments."""
        args = self.arg_parser.parse_args()

        self.test_for_help()
        return self.arg_parser.parse_args()

    @classmethod
    def get_config(cls, config_class):
        arg_parser = cls()

        # Create Config from the command line arguments.
        return config_class(arg_parser.parse_args())


if __name__ == "__main__":
    main()

# End of file.
