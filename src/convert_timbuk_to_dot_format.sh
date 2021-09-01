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
OUT=""

# Handle given arguments.
while getopts :i:po:t:v:n:h o; do
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
    p) # Print the output dot format FA.
        PRINT=true;
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
    n) # Amount of path elements to keep for output with '-o <dir>' parameter set.
        if [ -z "$OPTARG" ]; then # Parameter '-n' without given number or elements to keep following '-n'.
            print_stderr "Invalid flag: -n <number_of_elements>."
            exit 1;
        else
            NUMBER_OF_ELEMENTS="$OPTARG";
        fi
        ;;
    o) # Output finite automaton file in dot format.
        if test ! -z "$OPTARG" ; then # Parameter -o with given output file following '-o'.
            OUT="$OPTARG";
        fi
        ;;
    h) # Help.
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

if test ! "$PRINT" ; then
    if test ! -z "$OUT" ; then # Specified '-o' path.
        if test -d "$OUT" ; then # Store output to file in the goven directory with optional directory depth.
            # Double 'rev' trick taken from answer on SO by ACK_stoverflow: https://stackoverflow.com/a/31728689.
            F_FA_DOT="$(echo "$F_FA_TIMBUK" | rev | cut -d'/' -f-"$NUMBER_OF_ELEMENTS" | rev)";
            F_FA_DOT=""${OUT%%*(/)}"/"$F_FA_DOT".dot";
        else # Store output to new file.
            F_FA_DOT="$OUT";
        fi
    else # Given '-o' paramter without any optional argument.
        # Store result in the same directory as input Timbuk format FA file.
        F_FA_DOT=""$F_FA_TIMBUK".dot";
    fi

    # Create file inside desired subdirectories, if specified.
    mkdir --parents "${F_FA_DOT%/*}" && touch "$F_FA_DOT";
fi

# Convert given finite automaton in Timbuk format to dot format and store the result in a specified path.
"$F_TIMBUK2VTF" --fa "$F_FA_TIMBUK" | "$F_VTF2DOT" > "$F_FA_DOT";

# End of file run.sh.
