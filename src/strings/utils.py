"""Utility functions for pattern matching algorithms.

This module provides common utility functions used by different pattern matching
algorithms like KMP and Aho-Corasick.
"""

from strings.dfa import DFA, TransitionType

def compute_state_transitions(
    dfa: DFA, state_index: int, alphabets: str, fail_function_value: int
) -> None:
    """Compute and add transitions for a state based on its failure function.

    Args:
        dfa: The DFA to add transitions to
        state_index: The current state index
        alphabets: The set of possible characters
        fail_function_value: The failure function value for the current state
    """
    for symbol in alphabets:
        if not dfa.transition(state_index, symbol):
            dfa.add_transition(
                from_state=state_index,
                to_state=dfa.transition(fail_function_value, symbol) or 0,
                symbol=symbol,
                transition_type=TransitionType.FAILURE,
            )
