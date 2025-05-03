#!/usr/bin/env python3
"""Command-line interface for efficient pattern matching algorithms.

This module provides a unified command-line interface for string pattern matching
using automaton-based algorithms (KMP and Aho-Corasick). It supports building
pattern matching automata, searching for patterns in text, and flexible output formats.

Features:
- Single pattern matching (KMP) and multiple pattern matching (Aho-Corasick)
- Building and saving automata (DFAs) for later reuse
- Reading patterns from command line or from pattern files
- Configurable performance options (precomputed transitions)
- Multiple output formats (text or CSV)

Examples:
  # Build an Aho-Corasick DFA from command-line patterns
  $ python mpattern.py strbuild --patterns ABABC BCDEF DEFGH -o patterns.dfa

  # Build a KMP DFA from a single pattern
  $ python mpattern.py strbuild --patterns ABABC -a kmp -o kmp_pattern.dfa

  # Build a DFA from patterns in a file (one pattern per line)
  $ python mpattern.py strbuild --patterns-file dna_patterns.txt -o dna.dfa

  # Search using patterns directly with default text output
  $ python mpattern.py strsearch --patterns ABABC BCDEF -f genome.txt

    # Search using patterns directly with default text output and the text to search directly
  $ python mpattern.py strsearch --patterns ABABC BCDEF --text ABABC

  # Search using patterns from a file with CSV output
  $ python mpattern.py strsearch --patterns-file proteins.txt -f sequence.txt --output-format csv

  # Search using a pre-built DFA and save results to a file
  $ python mpattern.py strsearch --dfa-file patterns.dfa -f input.txt --output-file results.csv --output-format csv

  # Search from stdin and save the DFA for later use
  $ cat input.txt | python mpattern.py strsearch --patterns ABABC BCDEF --save-dfa patterns.dfa

  # Use KMP algorithm with explicit alphabet
  $ python mpattern.py strsearch --patterns ACGT -a kmp --alphabet ACGT -f dna.txt

  # Optimize for memory usage with --no-precompute
  $ python mpattern.py strsearch --patterns-file large_patterns.txt -f big_text.txt --no-precompute

Performance considerations:
- Aho-Corasick is for multiple patterns
- KMP is optimized for single pattern searches
- Precomputed transitions (default) use more memory but are faster
- Saved DFAs can be reused to avoid rebuilding the automaton
"""
import argparse
import sys

from strings.stringsapp import (
    read_input,
    build_dfa,
    search_with_patterns,
    search_with_dfa,
)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed comand line arguments
    """
    parser = argparse.ArgumentParser(
        description="Pattern matching using various algorithms"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    subparsers.required = True

    # String pattern matching commands
    # Build DFA command for string patterns
    strbuild_parser = subparsers.add_parser(
        "strbuild", help="Build a string pattern DFA and save it to a file"
    )
    pattern_group = strbuild_parser.add_mutually_exclusive_group(required=True)
    pattern_group.add_argument(
        "--patterns", nargs="+", help="One or more patterns to build the DFA from"
    )
    pattern_group.add_argument(
        "--patterns-file", help="File containing patterns, one per line"
    )
    strbuild_parser.add_argument(
        "-o", "--output", required=True, help="Output file to save the DFA"
    )
    strbuild_parser.add_argument(
        "-a",
        "--algorithm",
        choices=["kmp", "aho-corasick"],
        default="aho-corasick",
        help="Algorithm to use (default: aho-corasick)",
    )
    strbuild_parser.add_argument(
        "--no-precompute",
        action="store_true",
        help="Don't precompute transitions (uses less memory but may be slower)",
    )
    strbuild_parser.add_argument(
        "--alphabet", help="Explicitly specify the alphabet characters"
    )

    # Search command for string patterns
    strsearch_parser = subparsers.add_parser(
        "strsearch", help="Search for string patterns in text"
    )
    search_pattern_group = strsearch_parser.add_mutually_exclusive_group(required=True)
    search_pattern_group.add_argument(
        "--patterns", nargs="+", help="One or more patterns to search for"
    )
    search_pattern_group.add_argument(
        "--patterns-file", help="File containing patterns, one per line"
    )
    search_pattern_group.add_argument(
        "--dfa-file", help="Load a pre-built DFA from a JSON file"
    )
    
    # Input text source options - mutually exclusive
    text_source_group = strsearch_parser.add_mutually_exclusive_group(required=False)
    text_source_group.add_argument(
        "-f", "--file", help="Input file to search in"
    )
    text_source_group.add_argument(
        "-t", "--text", help="Text to search in (provided directly as an argument)"
    )
    
    strsearch_parser.add_argument(
        "-a",
        "--algorithm",
        choices=["kmp", "aho-corasick"],
        default="aho-corasick",
        help="Algorithm to use (default: aho-corasick)",
    )
    strsearch_parser.add_argument(
        "--no-precompute",
        action="store_true",
        help="Don't precompute transitions (uses less memory but may be slower)",
    )
    strsearch_parser.add_argument(
        "--alphabet", help="Explicitly specify the alphabet characters"
    )
    strsearch_parser.add_argument(
        "--save-dfa",
        help="Save the DFA to a JSON file (only when using --patterns or --patterns-file)",
    )
    strsearch_parser.add_argument(
        "--output-format",
        choices=["csv", "text"],
        default="text",
        help="Output format for search results (default: text)",
    )
    strsearch_parser.add_argument(
        "--output-file", help="File to write search results to (default: stdout)"
    )

    return parser.parse_args()

def get_input_text(args: argparse.Namespace) -> str:
    """Get the input text from file, command line argument, or stdin.
    
    Args:
        args: Command line arguments
        
    Returns:
        str: The input text to search in
    """
    if args.text is not None:
        # Text provided directly as a command line argument
        return args.text
    elif args.file is not None:
        # Text from a file
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    else:
        # Text from stdin
        return sys.stdin.read()

def read_patterns_from_file(file_path: str) -> list[str]:
    """Read patterns from a file, one pattern per line.

    Args:
        file_path: Path to the patterns file

    Returns:
        list[str]: List of patterns read from the file
    """
    with open(file_path, "r", encoding="utf-8") as f:
        if not (
            patterns := [line.strip() for line in f if line.strip()]
        ):  # Skip empty lines
            raise ValueError(f"No valid patterns found in {file_path}")
        return patterns


def print_results(
    matches: list[tuple[int, str]],
    output_format: str = "text",
    output_file: str | None = None,
) -> None:
    """Print search results in the specified format.

    Args:
        matches: List of matches
        output_format: Format to print results in ('csv' or 'text')
        output_file: File to write results to (None for stdout)
    """
    # Prepare output file or use stdout
    with open(output_file, "w", encoding="utf-8") if output_file else sys.stdout as f:
        # Print header for CSV format
        if output_format == "csv":
            print("position,pattern", file=f)

        # Aho-Corasick output (position, pattern)
        for pos, pattern in matches:
            if output_format == "csv":
                # Escape any commas in the pattern
                escaped_pattern = f'"{pattern}"' if "," in pattern else pattern
                print(f"{pos},{escaped_pattern}", file=f)
            else:
                print(f"Pattern '{pattern}' found at position {pos}", file=f)

        # Print summary (only for text format)
        if output_format == "text":
            print(f"\nTotal matches found: {len(matches)}", file=f)



def main() -> None:
    """Main entry point for the pattern matching CLI."""
    args = parse_arguments()

    if args.command == "strbuild":
        # Get patterns from command line or file
        if args.patterns:
            patterns = args.patterns
        else:  # args.patterns_file
            patterns = read_patterns_from_file(args.patterns_file)
            print(f"Loaded {len(patterns)} patterns from {args.patterns_file}")

        # Build a string pattern DFA and save it to a file
        build_dfa(
            patterns=patterns,
            output_file=args.output,
            algorithm=args.algorithm,
            precompute=not args.no_precompute,
            alphabet=args.alphabet,
        )

    elif args.command == "strsearch":
        # Read input text from file, command line argument, or stdin
        text = get_input_text(args)

        # Perform search using patterns, patterns file, or a pre-built DFA
        if args.dfa_file:
            # Using pre-built DFA
            matches = search_with_dfa(
                text=text, dfa_file=args.dfa_file, precompute=not args.no_precompute
            )

            # Print results
            print_results(
                matches=matches,
                output_format=args.output_format,
                output_file=args.output_file,
            )
        else:
            # Get patterns from command line or file
            if args.patterns:
                patterns = args.patterns
            else:  # args.patterns_file
                patterns = read_patterns_from_file(args.patterns_file)
                print(f"Loaded {len(patterns)} patterns from {args.patterns_file}")

            matches = search_with_patterns(
                text=text,
                patterns=patterns,
                algorithm=args.algorithm,
                precompute=not args.no_precompute,
                alphabet=args.alphabet,
                save_dfa=args.save_dfa,
            )

            # Print results
            print_results(
                matches=matches,
                output_format=args.output_format,
                output_file=args.output_file,
            )

if __name__ == "__main__":
    main()
