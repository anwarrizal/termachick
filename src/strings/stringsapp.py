"""String pattern matching utilities for command-line applications.

This module provides functions for building, saving, loading, and using
pattern matching automata (DFAs) for string pattern matching. It supports
both KMP (single pattern) and Aho-Corasick (multiple patterns) algorithms.

The functions in this module are designed to be used by command-line
applications for pattern matching tasks.
"""

import json
import sys
from strings.kmp import KMPMatcher
from strings.ahocorasick import AhoCorasickMatcher
from strings.dfa import DFA


def read_input(file_path: str | None = None) -> str:
    """Read input text from file or stdin.

    Args:
        file_path: Path to input file, or None to read from stdin

    Returns:
        str: Input text
    """
    if file_path:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return sys.stdin.read()


def build_dfa(
    patterns: list[str],
    output_file: str,
    algorithm: str = "aho-corasick",
    precompute: bool = True,
    alphabet: str | None = None,
) -> None:
    """Build a DFA from patterns and save it to a file.

    Args:
        patterns: List of patterns to build the DFA from
        output_file: Path to save the DFA to
        algorithm: Algorithm to use ('kmp' or 'aho-corasick')
        precompute: Whether to precompute transitions
        alphabet: Optional alphabet specification
    """
    if algorithm == "kmp":
        if len(patterns) > 1:
            print(
                "Warning: KMP only supports a single pattern. Using the first pattern."
            )

        # Create the matcher
        kmp_matcher = KMPMatcher(
            pattern=patterns[0], compute_transitions=precompute, alphabets=alphabet
        )

        # Save the DFA and additional data
        data = {
            "algorithm": "kmp",
            "pattern": patterns[0],
            "dfa": kmp_matcher.dfa.to_dict(),
            "fail_functions": kmp_matcher.fail_functions,
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"KMP DFA for pattern '{patterns[0]}' saved to {output_file}")

    else:  # aho-corasick
        # Create the matcher
        ac_matcher = AhoCorasickMatcher(
            patterns=patterns, compute_transitions=precompute, alphabets=alphabet
        )

        # Save the DFA and additional data
        data = {
            "algorithm": "aho-corasick",
            "patterns": patterns,
            "dfa": ac_matcher.dfa.to_dict(),
            "fail_functions": ac_matcher.fail_functions,
            "pattern_map": {str(k): v for k, v in ac_matcher.pattern_map.items()},
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Aho-Corasick DFA for {len(patterns)} patterns saved to {output_file}")


def load_matcher_from_file(
    file_path: str, precompute: bool = True
) -> KMPMatcher | AhoCorasickMatcher:
    """Load a matcher from a saved DFA file.

    Args:
        file_path: Path to the DFA file
        precompute: Whether to use precomputed transitions

    Returns:
        A matcher object (KMPMatcher or AhoCorasickMatcher)
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    algorithm = data.get("algorithm")

    if algorithm == "kmp":
        # Create a KMP matcher
        kmp_matcher = KMPMatcher.__new__(KMPMatcher)
        kmp_matcher.dfa = DFA.from_dict(data["dfa"])
        kmp_matcher.compute_transitions = precompute
        kmp_matcher.fail_functions = data["fail_functions"]

        return kmp_matcher

    if algorithm == "aho-corasick":
        # Create an Aho-Corasick matcher
        ac_matcher = AhoCorasickMatcher.__new__(AhoCorasickMatcher)
        ac_matcher.dfa = DFA.from_dict(data["dfa"])
        ac_matcher.compute_transitions = precompute
        ac_matcher.fail_functions = data["fail_functions"]
        ac_matcher.pattern_map = {int(k): v for k, v in data["pattern_map"].items()}

        return ac_matcher

    dfa = DFA.from_dict(data["dfa"])

    # Try to guess the algorithm based on the DFA structure
    if "pattern_map" in data:
        # This is likely Aho-Corasick
        ac_matcher = AhoCorasickMatcher.__new__(AhoCorasickMatcher)
        ac_matcher.dfa = dfa
        ac_matcher.compute_transitions = precompute
        ac_matcher.fail_functions = data.get(
            "fail_functions", [0] * (dfa.n_states() - 1)
        )
        ac_matcher.pattern_map = {int(k): v for k, v in data["pattern_map"].items()}
        return ac_matcher
    # This is likely KMP
    kmp_matcher = KMPMatcher.__new__(KMPMatcher)
    kmp_matcher.dfa = dfa
    kmp_matcher.compute_transitions = precompute
    kmp_matcher.fail_functions = data.get("fail_functions", [0] * (dfa.n_states() - 1))
    return kmp_matcher


def search_with_patterns(
    text: str,
    patterns: list[str],
    algorithm: str = "aho-corasick",
    precompute: bool = True,
    alphabet: str | None = None,
    save_dfa: str | None = None,
) -> list[tuple[int, str]]:
    """Search for patterns in text using the specified algorithm.

    Args:
        text: Input text to search in
        patterns: List of patterns to search for
        algorithm: Algorithm to use ('kmp' or 'aho-corasick')
        precompute: Whether to precompute transitions
        alphabet: Optional alphabet specification
        save_dfa: Path to save the DFA to a JSON file

    Returns:
        List of matches (positions for KMP, (position, pattern) tuples for Aho-Corasick)
    """
    if algorithm == "kmp":
        if len(patterns) > 1:
            print(
                "Warning: KMP only supports a single pattern. Using the first pattern."
            )

        # Create new matcher
        kmp_matcher = KMPMatcher(
            pattern=patterns[0], compute_transitions=precompute, alphabets=alphabet
        )

        # Save DFA if requested
        if save_dfa:
            data = {
                "algorithm": "kmp",
                "pattern": patterns[0],
                "dfa": kmp_matcher.dfa.to_dict(),
                "fail_functions": kmp_matcher.fail_functions,
            }

            with open(save_dfa, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            print(f"Saved KMP DFA to {save_dfa}")

        return list(kmp_matcher.search(text))

    # Create new matcher
    ac_matcher = AhoCorasickMatcher(
        patterns=patterns, compute_transitions=precompute, alphabets=alphabet
    )

    # Save DFA if requested
    if save_dfa:
        data = {
            "algorithm": "aho-corasick",
            "patterns": patterns,
            "dfa": ac_matcher.dfa.to_dict(),
            "fail_functions": ac_matcher.fail_functions,
            "pattern_map": {str(k): v for k, v in ac_matcher.pattern_map.items()},
        }

        with open(save_dfa, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Saved Aho-Corasick DFA to {save_dfa}")

    # Perform the search
    return list(ac_matcher.search(text))


def search_with_dfa(
    text: str,
    dfa_file: str,
    precompute: bool = True,
) -> list[tuple[int, str]]:
    """Search for patterns in text using a pre-built DFA.

    Args:
        text: Input text to search in
        dfa_file: Path to the DFA file
        precompute: Whether to use precomputed transitions

    Returns:
        List of matches (positions for KMP, (position, pattern) tuples for Aho-Corasick)
    """
    # Load matcher from file
    matcher = load_matcher_from_file(dfa_file, precompute)
    print(f"Loaded DFA from {dfa_file}")

    # Perform the search
    return list(matcher.search(text))
