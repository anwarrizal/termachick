"""Implementation of the Aho-Corasick string matching algorithm.

This module provides an efficient solution for simultaneously searching multiple
patterns in a text using a DFA-based approach with failure functions.

The main class AhoCorasickMatcher supports both pre-computed and on-the-fly
state transitions for pattern matching.
"""

from collections.abc import Generator
from strings.dfa import DFA, State, TransitionType


def alphabet_set_from_alphabets(alphabets: str | None, patterns: list[str]) -> set[str]:
    """Build an alphabet set from a list of patterns.

    Args:
        alphabets: A string containing the alphabet characters
        patterns: List of patterns

    Returns:
        A set of unique characters from the input string
    """
    # If alphabet is not provided, build it dynamically from the patterns
    if alphabets is None:
        alphabet_set = set()
        for pattern in patterns:
            for sym in pattern:
                alphabet_set.add(sym)
    else:
        alphabet_set = set(alphabets)
    return alphabet_set


def precompute_possible_transitions(
    dfa: DFA, index: int, alphabet_set: set[str], fail_functions: list[int]
) -> None:
    """Pre-compute all possible transitions for a given state.

    This function computes and stores all possible transitions for a given state
    based on the alphabet set. It is used to pre-compute transitions for all states
    in the DFA.

    Args:
        dfa (DFA): The DFA object.
        index (int): The index of the state for which transitions are pre-computed.
        alphabet_set (set[str]): The set of alphabet characters.
        fail_functions(list[int]): The fail functions.

    Raises:
        ValueError: If the transition from the current state to any alphabet character
            is not defined.
    """
    for a in alphabet_set:
        if dfa.transition(index, a) is None:
            if (to_state := dfa.transition(fail_functions[index - 1], a)) is None:
                raise ValueError(f"Invalid transition from {index} with {a}")
            dfa.add_transition(index, a, to_state, TransitionType.FAILURE)


class AhoCorasickMatcher:
    """An implementation of the Aho-Corasick string matching algorithm.

    This class implements a string matching automaton that can efficiently find multiple
    patterns in a text simultaneously. It uses a DFA (Deterministic Finite Automaton)
    with failure functions to perform pattern matching.

    Attributes:
        compute_transitions (bool): Controls whether state transitions are pre-computed
            or computed on-the-fly during pattern matching.
        dfa (DFA): The underlying deterministic finite automaton used for pattern matching.
        fail_functions (list[int]): Array of failure function values for each state.
        pattern_map (dict): Mapping of states to their corresponding pattern prefixes.

    Example:
        >>> patterns = ["ABABAC", "ABCABAB"]
        >>> matcher = AhoCorasickMatcher(patterns, compute_transitions=True)
        >>> text = "ABABCABABABABAC"
        >>> for pos, pattern in matcher.search(text):
        ...     print(f"Found {pattern} at position {pos}")
    """

    def _initialize_dfa(
        self, alphabets: set[str], patterns: list[str]
    ) -> tuple[DFA, dict]:
        """Create Trie structure from a given pattern

        Args:
            alphabets(str): The alphabets of the DFA
            patterns(list[str]): The list of patterns to match
        Return:
            Tuple of:
                - DFA: The DFA corresponds to the Trie
                - dict: The state name
        """

        dfa = DFA(alphabets=alphabets)
        dfa.add_state(is_accepting=False, is_initial=True)

        # Build trie structure by adding each pattern and store the pattern for each state
        pattern_map = {}
        for pattern in patterns:
            pattern_map.update(self._add_pattern(dfa, pattern))

        # Initialize failure transitions for the root state
        self._initialize_root(alphabets=alphabets, dfa=dfa)
        return dfa, pattern_map

    def _add_pattern(self, dfa: DFA, pattern: str) -> dict[State, str]:
        """Adds a pattern to the DFA by creating necessary states and transitions.
        Args:
            dfa (DFA): The deterministic finite automaton to add the pattern to
            pattern (str): The string pattern to be added to the DFA

        Returns:
            dict[State, str]: A mapping of states to their corresponding pattern prefixes
        """

        # Start from the initial state of the DFA
        if dfa.initial_state is None:
            raise ValueError("DFA has no initial state")
        state = dfa.initial_state
        pattern_map = {0: ""}

        # Try to follow existing transitions in the DFA for the current pattern
        i = 0
        new_state: int | None = None
        while i < len(pattern) and (new_state := dfa.transition(state, pattern[i])):
            i = i + 1
            state = new_state

        # If we couldn't follow existing transitions all the way (new_state is None)
        # or we need to add new states for the remaining characters
        if new_state is None:
            # Create new states for the remaining characters in the pattern
            for j in range(i, len(pattern)):
                # Store the current prefix of the pattern in the pattern map

                # Create a new state, marking it as accepting if it's the last character
                added_state = dfa.add_state(
                    is_accepting=(j == len(pattern) - 1), is_initial=False
                )
                pattern_map[added_state] = pattern[:j]

                # Add a transition from current state to new state with the current character
                dfa.add_transition(
                    from_state=state,
                    to_state=added_state,
                    symbol=pattern[j],
                    transition_type=TransitionType.SUCCESS,
                )
                state = added_state

            # Store the complete pattern in the pattern map for the final state
            pattern_map[state] = pattern[: j + 1]

        elif i == len(pattern):
            # We followed existing transitions and reached the end of the pattern
            # no need to create new state, and mark the final state as accepting
            dfa.set_accepting(new_state, True)
        return pattern_map

    def _initialize_root(self, alphabets: set[str], dfa: DFA) -> None:
        """Initialize failure transitions for the root state (state 0) of the DFA.

        Args:
            alphabets (set[str]): The set of possible characters in the alphabet
            dfa (DFA): The deterministic finite automaton to initialize

        This method adds self-loop failure transitions from the root state
        for any character that doesn't have an existing success transition.
        Only executes if compute_transitions is True.
        """
        if self.compute_transitions:
            for a in alphabets:
                if dfa.transition(0, a) is None:
                    dfa.add_transition(
                        from_state=0,
                        to_state=0,
                        symbol=a,
                        transition_type=TransitionType.FAILURE,
                    )

    def _initialize_top_level(
        self, sym: str, index: int, alphabets: set[str], dfa: DFA
    ) -> None:
        """Initializes the top-level states of the Aho-Corasick automaton (the states directly connected from the root).
        Args:
            sym(str): The transition from the root
            index(int): The index of the top level state
            alphabets (str): The set of possible characters in the alphabet
            dfa (DFA): The deterministic finite automaton to initialize

        """
        if self.compute_transitions:
            for a in alphabets:
                if not dfa.transition(index, a):
                    dfa.add_transition(
                        from_state=index,
                        to_state=index if sym == a else 0,
                        symbol=a,
                        transition_type=TransitionType.FAILURE,
                    )

    def __init__(
        self,
        patterns: list[str],
        compute_transitions: bool,
        alphabets: str | None = None,
    ) -> None:
        """Initialize the Aho-Corasick string matching automaton.
        Args:
            patterns: List of patterns to search for in the text
            compute_transitions: If True, pre-compute all state transitions.
                            If False, compute transitions on-the-fly
            alphabets: Optional string containing all possible characters.
                    If None, alphabet is derived from patterns

        The automaton consists of a DFA (Deterministic Finite Automaton) built from the patterns,
        along with failure functions for pattern matching.
        """
        if not patterns:
            raise ValueError("No patterns to match")
        for p in patterns:
            if not p:
                raise ValueError("Empty patterns")
        self.compute_transitions = compute_transitions

        alphabet_set = alphabet_set_from_alphabets(alphabets, patterns)

        # Initialize the DFA (trie structure) and get mapping of states to their corresponding patterns
        dfa, pattern_map = self._initialize_dfa(alphabet_set, patterns)

        # Initialize failure functions array for pattern matching
        # fail_functions[i] represents where to go when match fails at state i+1
        fail_functions = [0] * dfa.n_states()

        # Process each state in breadth-first order to build failure functions and transitions
        for parent, sym, index in list(dfa.bfs_traverse()):

            if parent == 0:
                # Special handling for states directly connected to root
                self._initialize_top_level(sym, index, alphabet_set, dfa)
            else:
                # For other states: compute failure function and additional transitions if needed
                fail_functions[index - 1] = (
                    dfa.transition(fail_functions[parent - 1], sym) or 0
                )
                if compute_transitions:
                    # Pre-compute all possible transitions for this state
                    precompute_possible_transitions(
                        dfa, index, alphabet_set, fail_functions
                    )

        self.fail_functions = fail_functions
        self.dfa = dfa
        self.pattern_map = pattern_map

    def search(self, s: str) -> Generator[tuple[int, str]]:
        """Search for all occurrences of patterns in the input text.

        Args:
            s (str): The input text to search through.

        Yields:
            tuple[int, str]: A tuple containing:
                - Position (index) where a pattern match begins
                - The matched pattern

        Example:
            >>> matcher = AhoCorasickMatcher(["ABABAC", "ABCABAB"], True)
            >>> for pos, pattern in matcher.search("ABABCABABABABAC"):
            ...     print(f"Found {pattern} at position {pos}")
        """
        state = 0
        if self.compute_transitions:
            # All transitions are pre-computed, allowing direct state transitions
            for index, sym in enumerate(s):
                if (new_state := self.dfa.transition(state, sym)) is None:
                    raise ValueError("Error in DFA definition")
                state = new_state

                if self.dfa.is_accepting_state(state):
                    pattern = self.pattern_map[state]
                    yield (index - len(pattern) + 1), pattern
        else:
            # Compute transitions on-the-fly using failure functions
            for index, sym in enumerate(s):
                if (new_state := self.dfa.transition(state, sym)) is not None:
                    state = new_state
                else:
                    # No direct transition found - follow failure links until we find a valid transition
                    fail_functions_index = (state - 1) if state > 0 else 0
                    transition_state = 0

                    # Keep following failure links until we either:
                    # 1. Find a valid transition for current character, or
                    # 2. Reach the root state (fail_functions_index = 0)
                    while (
                        not (
                            transition_state := self.dfa.transition(
                                self.fail_functions[fail_functions_index], sym
                            )
                            or 0
                        )
                        and fail_functions_index > 0
                    ):
                        fail_functions_index = self.fail_functions[fail_functions_index]

                    # Cache the computed transition for future use
                    if self.dfa.transition(state, sym) is None:
                        self.dfa.add_transition(
                            state,
                            symbol=sym,
                            to_state=transition_state,
                            transition_type=TransitionType.FAILURE,
                        )

                    state = transition_state

                if self.dfa.is_accepting_state(state):
                    pattern = self.pattern_map[state]
                    yield (index - len(pattern) + 1), pattern
