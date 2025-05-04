"""Implementation of Knuth-Morris-Pratt string matching algorithm using DFA.

This module provides a KMPMatcher class that implements pattern matching using either
precomputed state transitions or failure functions for memory/speed tradeoffs.
"""

from collections.abc import Generator
from strings.dfa import DFA, TransitionType


def search_lazy_transition(
    dfa: DFA, fail_functions: list[int], pattern: str, s: str
) -> Generator[tuple[int, str]]:
    """Searches for pattern matches in text using KMP algorithm.

    Implements KMP pattern matching algorithm to find all occurrences of the pattern
    in the input text. Uses either precomputed transitions or failure function
    based on initialization.
    Then, during the search, the transition is added on the fly.

    Args:
        s: Input text to search in
        dfa: The DFA representing the automaton for the success path search
        pattern: The pattern
        fail_functions: The fail functions that augment the DFA

    Yields:
        int: Starting positions of pattern matches in the text
        str: The pattern

    Example:
        >>> matcher = KMPMatcher("ABC", compute_transitions=True)
        >>> list(matcher.search("ABCABCABC"))
        [0, 3, 6]
    """
    state = 0
    for index, sym in enumerate(s):
        if (new_state := dfa.transition(state, sym)) is not None:
            state = new_state
        else:
            fail_functions_index = (state - 1) if state > 0 else 0
            transition_state: int = 0

            # Follow fail functions or reach root
            while (
                not (
                    transition_state := dfa.transition(
                        fail_functions[fail_functions_index], sym
                    )
                    or 0
                )
                and fail_functions_index > 0
            ):
                fail_functions_index = fail_functions[fail_functions_index]

            # Cache the computed transition for future use
            if dfa.transition(state, sym) is None:
                dfa.add_transition(
                    state,
                    symbol=sym,
                    to_state=transition_state or 0,
                    transition_type=TransitionType.FAILURE,
                )

            state = transition_state

        if dfa.is_accepting_state(state):
            yield index - state + 1, pattern


class KMPMatcher:
    """Implements Knuth-Morris-Pratt (KMP) string matching algorithm.

    This class implements the KMP pattern matching algorithm using a deterministic
    finite automaton (DFA) approach. It can be configured to either precompute all
    transitions or lazily builds the DFA using failure functions for state transitions.

    Attributes:
        compute_transitions (bool): Whether to precompute all state transitions
        fail_functions (list[int]): Array storing failure function values. The index corresponds to the state - 1,
             because there is no fail_functions for 0th state.
        dfa (DFA): Deterministic finite automaton for pattern matching

    Args:
        pattern (str): The pattern string to search for
        compute_transitions (bool): Whether to precompute all state transitions
        alphabets (str | None, optional): Set of valid input symbols. If None,
            derived from pattern. Defaults to None.

    Example:
        >>> # Create KMP matcher with precomputed transitions
        >>> matcher = KMPMatcher("ABC", compute_transitions=True)
        >>> # Find all occurrences of pattern
        >>> list(matcher.search("ABCABCABC"))
        [0, 3, 6]

    Notes:
        - Using compute_transitions=True precomputes all state transitions for faster
          matching but requires more memory
        - Using compute_transitions=False uses failure functions which requires less
          memory but may be slower for matching
    """

    def _initialize_dfa(self, alphabets: set[str], pattern: str) -> DFA:
        """Initializes KMP automaton for pattern matching.

        Creates and configures a DFA for KMP pattern matching with states
        corresponding to pattern prefixes.

        Args:
            alphabets: Set of valid input symbols
            pattern: Pattern string to search for

        Returns:
            DFA: Configured automaton for pattern matching

        Raises:
            ValueError: If pattern contains characters not in alphabet
        """
        dfa = DFA(alphabets=alphabets)
        # Creates the states
        dfa.add_state(is_accepting=(0 == len(pattern)), is_initial=True)
        for index, sym in enumerate(pattern):
            dfa.add_state(
                is_accepting=(index == len(pattern) - 1), is_initial=index == 0
            )
            if index < len(pattern):
                dfa.add_transition(
                    from_state=index,
                    to_state=index + 1,
                    symbol=sym,
                    transition_type=TransitionType.SUCCESS,
                )
        if self.compute_transitions:
            # Initializes the state 0
            for a in alphabets:
                if not dfa.transition(0, a):
                    dfa.add_transition(
                        from_state=0,
                        to_state=0,
                        symbol=a,
                        transition_type=TransitionType.FAILURE,
                    )
        return dfa

    def __init__(
        self, pattern: str, compute_transitions: bool, alphabets: str | None = None
    ) -> None:
        if not pattern:
            raise ValueError("Empty pattern")
        self.compute_transitions = compute_transitions

        alphabet_set = set(alphabets) if alphabets else set(pattern)

        dfa = self._initialize_dfa(alphabet_set, pattern)

        # define fail _functions and transitions
        fail_functions = [0] * len(pattern)
        for index in range(1, len(pattern) + 1):
            if compute_transitions:
                # set the transitions
                for a in alphabet_set:
                    if not dfa.has_transition(index, a):
                        to_state = dfa.transition(fail_functions[index - 1], a) or 0
                        dfa.add_transition(
                            index, a, to_state, transition_type=TransitionType.FAILURE
                        )
            # compute the next fail function
            if index < len(pattern):
                fail_functions[index] = (
                    dfa.transition(fail_functions[index - 1], pattern[index]) or 0
                )
        self.fail_functions = fail_functions
        self.dfa = dfa
        self.pattern = pattern

    def search(self, s: str) -> Generator[tuple[int, str]]:
        """Searches for pattern matches in text using KMP algorithm.

        Implements KMP pattern matching algorithm to find all occurrences of the pattern
        in the input text. Uses either precomputed transitions or failure function
        based on initialization.

        Args:
            s: Input text to search in

        Yields:
            Tuple of:
                - int: Starting positions of pattern matches in the text
                - str: The pattern

        Example:
            >>> matcher = KMPMatcher("ABC", compute_transitions=True)
            >>> list(matcher.search("ABCABCABC"))
            [0, 3, 6]
        """
        state = 0
        if self.compute_transitions:
            for index, sym in enumerate(s):
                # Update state based on current character
                if (new_state := self.dfa.transition(state, sym)) is None:
                    raise ValueError("Error in DFA definition")
                state = new_state
                # Found a match
                if self.dfa.is_accepting_state(state):
                    yield index - state + 1, self.pattern
        else:
            yield from search_lazy_transition(
                self.dfa, self.fail_functions, self.pattern, s
            )
