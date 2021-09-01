#!/usr/bin/env sh

# ====================================================
# file name: convert_timbuk_to_dot.sh
#
# Base script for converting FA in Timbuk format to dot format.
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
F_FA_TIMBUK=""
F_FA_DOT="/dev/stdout"
F_TIMBUK2VTF=""
F_VTF2DOT=""

# Handle given arguments.
while getopts :i:o:t:v:h o; do
    case "$o" in
    i) # input FA file in Timbuk format.
        if [ -z "$OPTARG" ]; then # Parameter '-i' without given finite automaton in Timbuk format file following '-i'.
            print_stderr "Invalid flag: -i <finite_automaton_timbuk_file>."
            exit 1;
        else
            if test -f "$OPTARG"; then
                F_FA_TIMBUK="$OPTARG"
            else
                print_stderr "No such file: $OPTARG"
                exit 1;
            fi
        fi
        ;;
    t) # Timbuk to vtf converter script file.
        if [ -z "$OPTARG" ]; then # Parameter '-t' without given Timbuk to vtf converter script file following '-t'.
            print_stderr "Invalid flag: -t <timbuk_to_vtf_converter_file>."
            exit 1;
        else
            if test -f "$OPTARG"; then
                F_TIMBUK2VTF="$OPTARG"
            else
                print_stderr "No such file: $OPTARG"
                exit 1;
            fi
        fi
        ;;
    v) # vtf to dot converter script file.
        if [ -z "$OPTARG" ]; then # Parameter '-v' without given vtf to dot converter script file following '-v'.
            print_stderr "Invalid flag: -v <vtf_to_dot_converter_file>."
            exit 1;
        else
            if test -f "$OPTARG"; then
                F_VTF2DOT="$OPTARG"
            else
                print_stderr "No such file: $OPTARG"
                exit 1;
            fi
        fi
        ;;
    o) # Output finite automaton file in dot format.
        if [ -z "$OPTARG" ]; then # Parameter -o without given output file following '-o'.
            F_FA_DOT=""$(basename "$F_FA_TIMBUK")".dot"
        else
            F_FA_DOT="$OPTARG"
        fi
        ;;
    h) # help #TODO
        printf "Usage: ./convert_timbuk_to_dot_format.sh [-i finite_automaton_timbuk_file] [-o finite_automaton_dot_file]\n\n"
        echo "   [-i finite_automaton_timbuk_file] –– set finite_automaton_timbuk_file file to be Timbuk description of finite automaton to be converted."
        echo "   [-o finite_automaton_dot_file] –– set output file containing the given Timbuk finite automaton in dot format"
        exit 0
        ;;
    *) # invalid flag
        print_stderr "Invalid flag: $*."
        exit 1;
        ;;
    esac
done

"$F_TIMBUK2VTF" --fa "$F_FA_TIMBUK" | "$F_VTF2DOT" > "$F_FA_DOT";

# End of file run.sh.
