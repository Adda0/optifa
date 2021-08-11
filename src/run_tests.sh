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

F_TIME_CSV="tmp_time_csv"
F_DATA_OUT="tmp_data_out"

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



# Print basic information about initial automata.
echo -n ""$F_FA_A_ORIG","$F_FA_B_ORIG"," >> "$F_OUTPUT"
python3 print_automata_sizes.py "$F_FA_A_ORIG" "$F_FA_B_ORIG" >> "$F_OUTPUT";

# Run every algorithm version:
## Emptiness tests:
### Basic algorithm:
hyperfine "python3 -u generate_basic_product.py --break_when_final $F_FA_A_ORIG $F_FA_B_ORIG > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -w 1 -r 3;

cat "$F_DATA_OUT" >> "$F_OUTPUT";
echo -n "$(cut --complement -f 1 -d, "$F_TIME_CSV")" > "$F_TIME_CSV"
echo -n "$(tail -n +2 "$F_TIME_CSV")" > "$F_TIME_CSV"
cat "$F_TIME_CSV" >> "$F_OUTPUT";

### Length abstraction:
# - With SMT solver:
hyperfine "python3 -u resolve_satisfiability_length_abstraction.py --smt --break_when_final $F_FA_A_ORIG $F_FA_B_ORIG > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -w 1 -r 3;

cat "$F_DATA_OUT" >> "$F_OUTPUT";
echo -n "$(cut --complement -f 1 -d, "$F_TIME_CSV")" > "$F_TIME_CSV"
echo -n "$(tail -n +2 "$F_TIME_CSV")" > "$F_TIME_CSV"
cat "$F_TIME_CSV" >> "$F_OUTPUT";

# - Without SMT solver:
hyperfine "python3 -u resolve_satisfiability_length_abstraction.py --break_when_final $F_FA_A_ORIG $F_FA_B_ORIG > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -w 1 -r 3;

cat "$F_DATA_OUT" >> "$F_OUTPUT";
echo -n "$(cut --complement -f 1 -d, "$F_TIME_CSV")" > "$F_TIME_CSV"
echo -n "$(tail -n +2 "$F_TIME_CSV")" > "$F_TIME_CSV"
cat "$F_TIME_CSV" >> "$F_OUTPUT";



echo "" >> "$F_OUTPUT"; # End the current experiment results.


# End of file run.sh.
