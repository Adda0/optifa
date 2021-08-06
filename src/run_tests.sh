#!/usr/bin/env sh

# ====================================================
# file name: run_tests.sh
#
# Base script for running optimizing automata product construction and its emptiness test
# ====================================================
# project: Optimizing Automata Product Construction and Emptiness Test
# "Optimalizace automatové konstrukce produktu a testu prázdnosti jazyka"
#
# author: David Chocholatý (xchoch08), FIT BUT
# ====================================================

export POSIXLY_CORRECT=yes

# functions
print_stderr() { printf "%s\n" "$*" >&2; } # print message to stderr (newline character included): print_stderr "<message>"

# default files
F_FA_A_ORIG=""
F_FA_B_ORIG=""

# handle given arguments
# ./run.sh [-a finite_automaton_A] [-b finite_automaton_B] [-o output]"
while getopts :a:b:o:h o; do
    case "$o" in
    # input files
    a) # finite_automaton_A file
        if [ -z "$OPTARG" ]; then # parameter -a without given finite_automaton_A file following '-a'
            print_stderr "Invalid flag: -a <finite_automaton_A_file>."
            exit 1;
        else
            if test -f "$OPTARG"; then
                F_FA_A_ORIG="$OPTARG"
            else
                print_stderr "No such file: $OPTARG"
                exit 1;
            fi
        fi
        ;;
    b) # finite_automaton_B file
        if [ -z "$OPTARG" ]; then # parameter -b without given finite_automaton_A file following '-b'
            print_stderr "Invalid flag: -b <finite_automaton_B_file>."
            exit 1;
        else
            if test -f "$OPTARG"; then
                F_FA_B_ORIG="$OPTARG"
            else
                print_stderr "No such file: $OPTARG"
                exit 1;
            fi
        fi
        ;;
    # output files
    o) # result //TODO
        if [ -z "$OPTARG" ]; then # parameter -o without given output file following '-o'
            print_stderr "Invalid flag: -o <output_file>."
            exit 1;
        else
            F_OUTPUT="$OPTARG"
        fi
        ;;
    h) # help #TODO
        printf "Usage: ./run.sh [-a finite_automaton_A_file] [-b finite_automaton_B_file] [-o output]\n\n"
        echo "   [-a finite_automaton_A_file] –– set finite_automaton_A file to be Timbuk description of finite automaton A"
        echo "   [-b finite_automaton_B_file] –– set finite_automaton_B file to be Timbuk description of finite automaton B"
        echo "   [-o output_file] –– set output file containing the result"
        exit 0
        ;;
    *) # invalid flag
        print_stderr "Invalid flag: $*."
        exit 1;
        ;;
    esac
done

# Create results file.
touch "$F_OUTPUT";

# Start hyperfine.
hyperfine "python3 -u resolve_satisfiability.py $F_FA_A_ORIG $F_FA_B_ORIG > tmp_output" --export-csv tmp_time_csv -u second -w 1 -r 3;

# Append to the results file.
cat tmp_output >> "$F_OUTPUT";
cat tmp_time_csv >> "$F_OUTPUT";




# End of file run.sh.
