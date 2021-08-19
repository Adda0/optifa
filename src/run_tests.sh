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

append_output() {
    cat "$F_DATA_OUT" >> "$F_OUTPUT";
    echo -n "$(cut --complement -f 1 -d, "$F_TIME_CSV")" > "$F_TIME_CSV"
    echo -n "$(tail -n +2 "$F_TIME_CSV")" > "$F_TIME_CSV"
    cat "$F_TIME_CSV" >> "$F_OUTPUT";
    echo -n "," >> "$F_OUTPUT";
}

# default files
F_FA_A_ORIG=""
F_FA_B_ORIG=""

F_TIME_CSV="tmp_time_csv"
F_DATA_OUT="tmp_data_out"
F_FA_A_LOADED="tmp_automaton_a"
F_FA_B_LOADED="tmp_automaton_b"
F_TESTED_COMBINATIONS="tested_combinations"

# handle given arguments
# ./run.sh [-a finite_automaton_A] [-b finite_automaton_B] [-o output]"
while getopts :a:b:o:t:h o; do
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
    t) # Tested combinations
        if [ -z "$OPTARG" ]; then # Parameter -t without given output file following '-t'.
            print_stderr "Invalid flag: -t <tested_combinations_file>."
            exit 1;
        else
            F_TESTED_COMBINATIONS="$OPTARG"
        fi
        ;;
    h) # help #TODO
        printf "Usage: ./run.sh [-a finite_automaton_A_file] [-b finite_automaton_B_file] [-o output]\n\n"
        echo "   [-a finite_automaton_A_file] –– set finite_automaton_A file to be Timbuk description of finite automaton A"
        echo "   [-b finite_automaton_B_file] –– set finite_automaton_B file to be Timbuk description of finite automaton B"
        echo "   [-o output_file] –– set output file containing the result"
        echo "   [-t tested_combinations_file] –– set output file containing the tested combinations"
        exit 0
        ;;
    *) # invalid flag
        print_stderr "Invalid flag: $*."
        exit 1;
        ;;
    esac
done


# Create results file.
if [ ! -f "$F_OUTPUT" ]; then
    touch "$F_OUTPUT";

    echo -n "Larger automaton,Smaller automaton," >> "$F_OUTPUT";
    echo -n "L.states,L.initial,L.final,L.transitions,S.states,S.initial,S.final,S.transitions," >> "$F_OUTPUT";
    echo -n "ET.B.states,ET.B.final,ET.B.mean,ET.B.stddev,ET.B.median,ET.B.user,ET.B.system,ET.B.min,ET.B.max," >> "$F_OUTPUT";
    echo -n "ET.L.smt.checked,ET.L.smt.processed,ET.L.smt.sat,ET.L.smt.false,ET.L.smt.skipped,ET.L.smt.l.lasso,ET.L.smt.s.lasso,ET.L.smt.states,ET.L.smt.final,ET.L.smt.mean,ET.L.smt.stddev,ET.L.smt.median,ET.L.smt.user,ET.L.smt.system,ET.L.smt.min,ET.L.smt.max," >> "$F_OUTPUT";
    echo -n "ET.L.smt_free.checked,ET.L.smt_free.processed,ET.L.smt_free.sat,ET.L.smt_free.false,ET.L.smt_free.skipped,ET.L.smt_free.l.lasso,ET.L.smt_free.s.lasso,ET.L.smt_free.states,ET.L.smt_free.final,ET.L.smt_free.mean,ET.L.smt_free.stddev,ET.L.smt_free.median,ET.L.smt_free.user,ET.L.smt_free.system,ET.L.smt_free.min,ET.L.smt_free.max," >> "$F_OUTPUT";
    echo -n "ET.P.forward.checked,ET.P.forward.processed,ET.P.forward.sat,ET.P.forward.false,ET.P.forward.skipped,ET.P.forward.states,ET.P.forward.final,ET.P.forward.mean,ET.P.forward.stddev,ET.P.forward.median,ET.P.forward.user,ET.P.forward.system,ET.P.forward.min,ET.P.forward.max," >> "$F_OUTPUT";
    echo -n "ET.P.backward.checked,ET.P.backward.processed,ET.P.backward.sat,ET.P.backward.false,ET.P.backward.skipped,ET.P.backward.states,ET.P.backward.final,ET.P.backward.mean,ET.P.backward.stddev,ET.P.backward.median,ET.P.backward.user,ET.P.backward.system,ET.P.backward.min,ET.P.backward.max," >> "$F_OUTPUT";
    echo -n "ET.P.no_lengths.checked,ET.P.no_lengths.processed,ET.P.no_lengths.sat,ET.P.no_lengths.false,ET.P.no_lengths.skipped,ET.P.no_lengths.states,ET.P.no_lengths.final,ET.P.no_lengths.mean,ET.P.no_lengths.stddev,ET.P.no_lengths.median,ET.P.no_lengths.user,ET.P.no_lengths.system,ET.P.no_lengths.min,ET.P.no_lengths.max," >> "$F_OUTPUT";
    echo -n "ET.C.checked,ET.C.processed,ET.C.sat,ET.C.false,ET.C.skipped,ET.C.len.sat,ET.C.len.unsat,ET.C.par.sat,ET.C.par.unsat,ET.C.l.lasso,ET.C.s.lasso,ET.C.states,ET.C.final,ET.C.mean,ET.C.stddev,ET.C.median,ET.C.user,ET.C.system,ET.C.min,ET.C.max," >> "$F_OUTPUT";
    echo -n "FP.B.states,FP.B.final,FP.B.mean,FP.B.stddev,FP.B.median,FP.B.user,FP.B.system,FP.B.min,FP.B.max," >> "$F_OUTPUT";
    echo -n "FP.L.smt.checked,FP.L.smt.processed,FP.L.smt.sat,FP.L.smt.false,FP.L.smt.skipped,FP.L.smt.l.lasso,FP.L.smt.s.lasso,FP.L.smt.states,FP.L.smt.final,FP.L.smt.mean,FP.L.smt.stddev,FP.L.smt.median,FP.L.smt.user,FP.L.smt.system,FP.L.smt.min,FP.L.smt.max," >> "$F_OUTPUT";
    echo -n "FP.L.smt_free.checked,FP.L.smt_free.processed,FP.L.smt_free.sat,FP.L.smt_free.false,FP.L.smt_free.skipped,FP.L.smt_free.l.lasso,FP.L.smt_free.s.lasso,FP.L.smt_free.states,FP.L.smt_free.final,FP.L.smt_free.mean,FP.L.smt_free.stddev,FP.L.smt_free.median,FP.L.smt_free.user,FP.L.smt_free.system,FP.L.smt_free.min,FP.L.smt_free.max," >> "$F_OUTPUT";
    echo -n "FP.P.forward.checked,FP.P.forward.processed,FP.P.forward.sat,FP.P.forward.false,FP.P.forward.skipped,FP.P.forward.states,FP.P.forward.final,FP.P.forward.mean,FP.P.forward.stddev,FP.P.forward.median,FP.P.forward.user,FP.P.forward.system,FP.P.forward.min,FP.P.forward.max," >> "$F_OUTPUT";
    echo -n "FP.P.backward.checked,FP.P.backward.processed,FP.P.backward.sat,FP.P.backward.false,FP.P.backward.skipped,FP.P.backward.states,FP.P.backward.final,FP.P.backward.mean,FP.P.backward.stddev,FP.P.backward.median,FP.P.backward.user,FP.P.backward.system,FP.P.backward.min,FP.P.backward.max," >> "$F_OUTPUT";
    echo -n "FP.P.no_lengths.checked,FP.P.no_lengths.processed,FP.P.no_lengths.sat,FP.P.no_lengths.false,FP.P.no_lengths.skipped,FP.P.no_lengths.states,FP.P.no_lengths.final,FP.P.no_lengths.mean,FP.P.no_lengths.stddev,FP.P.no_lengths.median,FP.P.no_lengths.user,FP.P.no_lengths.system,FP.P.no_lengths.min,FP.P.no_lengths.max," >> "$F_OUTPUT";
    echo -n "FP.C.checked,FP.C.processed,FP.C.sat,FP.C.false,FP.C.skipped,FP.C.len.sat,FP.C.len.unsat,FP.C.par.sat,FP.C.par.unsat,FP.C.l.lasso,FP.C.s.lasso,FP.C.states,FP.C.final,FP.C.mean,FP.C.stddev,FP.C.median,FP.C.user,FP.C.system,FP.C.min,FP.C.max," >> "$F_OUTPUT";
fi

if [ ! -f "$F_TESTED_COMBINATIONS" ]; then
    touch "$F_TESTED_COMBINATIONS";
    echo "Larger automaton,Smaller automaton," > "$F_TESTED_COMBINATIONS";
fi

# Start new experiment on a new line.
echo "" >> "$F_OUTPUT";

# Print basic information about initial automata.
AUTOMATA_PATHS="$(python3 print_automata_paths.py "$F_FA_A_ORIG" "$F_FA_B_ORIG")"
echo -n "$AUTOMATA_PATHS" >> "$F_OUTPUT";
grep -qxF "$AUTOMATA_PATHS" "$F_TESTED_COMBINATIONS" || echo "$AUTOMATA_PATHS" >> "$F_TESTED_COMBINATIONS";
python3 print_automata_sizes.py "$F_FA_A_ORIG" "$F_FA_B_ORIG" >> "$F_OUTPUT";

F_TIME_CSV="tmp_time_csv_"$F_OUTPUT""
F_DATA_OUT="tmp_data_out_"$F_OUTPUT""
F_FA_A_LOADED="tmp_automaton_a_"$F_OUTPUT""
F_FA_B_LOADED="tmp_automaton_b_"$F_OUTPUT""

# Load automata to a Python object.
load_automata.py -a "$F_FA_A_ORIG" -b "$F_FA_B_ORIG" --out_a "$F_FA_A_LOADED" --out_b "$F_FA_B_LOADED";

# Run every algorithm version:
## Emptiness tests:
### Basic algorithm:
hyperfine "python3 generate_basic_product.py --break_when_final "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

### Length abstraction:
# - With SMT solver:
hyperfine "python3 resolve_satisfiability_length_abstraction.py --smt --break_when_final "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

# - Without SMT solver:
hyperfine "python3 resolve_satisfiability_length_abstraction.py --break_when_final "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

### Parikh image:
# - Forward lengths computation:
#hyperfine "python3 resolve_satisfiability_parikh_image.py --forward_lengths --break_when_final "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
#append_output;
echo -n ",,,,,,,,,,,,,," >> "$F_OUTPUT";

# - Backward lengths computation:
hyperfine "python3 resolve_satisfiability_parikh_image.py --break_when_final "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

# - Without legths computation:
hyperfine "python3 resolve_satisfiability_parikh_image.py --no_z_constraints --break_when_final "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

### Combined algorithms:
hyperfine "python3 resolve_satisfiability_combined.py --no_z_constraints --break_when_final "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -w 1 -r 2;
append_output;

## Full product generation:
### Basic algorithm:
hyperfine "python3 generate_basic_product.py "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

### Length abstraction:
# - With SMT solver:
hyperfine "python3 resolve_satisfiability_length_abstraction.py --smt "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

# - Without SMT solver:
hyperfine "python3 resolve_satisfiability_length_abstraction.py "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

### Parikh image:
# - Forward lengths computation:
#hyperfine "python3 resolve_satisfiability_parikh_image.py --forward_lengths "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
#append_output;
echo -n ",,,,,,,,,,,,,," >> "$F_OUTPUT";

# - Backward lengths computation:
hyperfine "python3 resolve_satisfiability_parikh_image.py "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

# - Without legths computation:
hyperfine "python3 resolve_satisfiability_parikh_image.py --no_z_constraints "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -r 2;
append_output;

### Combined algorithms:
hyperfine "python3 resolve_satisfiability_combined.py --no_z_constraints "$F_FA_A_LOADED" "$F_FA_B_LOADED" > "$F_DATA_OUT"" --export-csv "$F_TIME_CSV" -u second -w 1 -r 2;
append_output;

# End of file run.sh.
