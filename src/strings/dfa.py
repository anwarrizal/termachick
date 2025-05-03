"""Implementation of a Deterministic Finite Automaton (DFA) for pattern matching and state machine processing.

This module provides a DFA implementation with support for:
- State management and transitions
- Success and failure transition paths
- Accepting/non-accepting state classification
- Breadth-first traversal capabilities
- Complete alphabet validation
- Serialization and deserialization to/from JSON

Classes:
    TransitionType: Enum for classifying transition types (success/failure)
    DFA: Main implementation of the Deterministic Finite Automaton

Type Aliases:
    State: Integer representation of DFA states
"""

from enum import Enum
from collections import deque
from collections.abc import Generator
from typing import Any

State = int


class TransitionType(Enum):
    """Enumeration for types of transitions in the DFA"""

    SUCCESS = "success"  # Forward/success transition
    FAILURE = "failure"  # Failure/fallback transition


class DFA:
    """A Deterministic Finite Automaton (DFA) implementation.

    This class implements a DFA with support for state management, transitions,
    and state classification (accepting/non-accepting). The automaton supports
    both success and failure transitions between states.

    Key features:
    - Dynamic state addition and management
    - Support for accepting and initial states
    - Transition management with success/failure classification
    - BFS traversal capability
    - Complete alphabet validation for transitions

    The states are represented as integers, starting from 0.
    """

    def __init__(self, alphabets: set[str]):
        """Initialize an empty DFA
        Args:
            alphabets (set[str]): The alphabets of the DFA
        """
        self.states: int | None = None  # The states are numbered from 0 to self.states
        self.alphabets: set[str] = alphabets
        self.transitions: dict[State, dict[str, State]] = {}
        self.transition_types: dict[State, dict[str, TransitionType]] = {}
        self.initial_state: State | None = None
        self.accepting_states: set[State] = set()

    def add_state(self, is_accepting: bool = False, is_initial: bool = False) -> State:
        """Add a new state to the DFA

        Args:
            is_accepting: Whether this is an accepting state
            is_initial: Whether this is the initial state

        Returns:
            State: The newly created state

        Raises:
            ValueError: If an initial state already exists and trying to add another
        """
        self.states = 0 if self.states is None else self.states + 1
        if is_initial:
            if self.initial_state:
                raise ValueError("DFA already has an initial state")
            self.initial_state = self.states
        if is_accepting:
            self.accepting_states.add(self.states)

        return self.states

    def bfs_traverse(self) -> Generator[tuple[State, str, State]]:
        """Performs a breadth-first traversal of the DFA starting from the initial state.

        Yields:
            State: Each state in BFS order

        Raises:
            ValueError: If DFA has no initial state
        """
        if self.initial_state is None:
            raise ValueError("DFA has no initial state")

        first_level_children = [
            (self.initial_state, chr, s)
            for chr, s in list(self.transitions[self.initial_state].items())
            if s != self.initial_state
        ]
        queue = deque(first_level_children)
        visited = set(first_level_children)

        # BFS traversal
        while queue:
            current_state = queue.popleft()
            yield current_state

            # Explore all transitions from current state
            if current_state[2] in self.transitions:
                for sym, next_state in self.transitions[current_state[2]].items():
                    if (current_state[2], sym, next_state) not in visited:
                        queue.append((current_state[2], sym, next_state))
                        visited.add((current_state[2], sym, next_state))

    def add_transition(
        self,
        from_state: State,
        symbol: str,
        to_state: State,
        transition_type: TransitionType = TransitionType.SUCCESS,
    ) -> None:
        """Adds a transition between states

        Args:
            from_state: Source state
            symbol: Transition symbol
            to_state: Destination state
            transition_type: Type of transition, whether it is a Success or Failure paths
        Raises:
            ValueError: If states don't exist or transition is already defined
        """
        if self.states is None:
            raise ValueError("No state")
        if from_state < 0 or from_state > self.states:
            raise ValueError(f"State {from_state} does not exist")
        if to_state < 0 or to_state > self.states:
            raise ValueError(f"State {to_state} does not exist")
        if symbol not in self.alphabets:
            raise ValueError(f"Symbol {symbol} does not exist {self.alphabets}")

        # Initialize the inner dictionaries if they don't exist
        if from_state not in self.transitions:
            self.transitions[from_state] = {}
            self.transition_types[from_state] = {}

        if symbol in self.transitions[from_state]:
            raise ValueError(
                f"Transition from {from_state} on symbol {symbol} already exists"
            )

        self.transitions[from_state][symbol] = to_state
        self.transition_types[from_state][symbol] = transition_type

    def add_accepting(self, state: State) -> None:
        """Adds a state as an accepting state.

        Args:
            state(State): the accepting state

        """
        if not self.states:
            raise ValueError("No state defined")
        if state < 0 or state > self.states:
            raise ValueError(f"State {state} does not exist")
        self.accepting_states.add(state)

    def set_accepting(self, state: State, accepting: bool) -> None:
        """Sets a state to be an accepting state.
        Args:
            state (State): The state
            accepting(bool): Whether the state is an accepting state or not.
        """
        if accepting:
            self.accepting_states.add(state)
        else:
            self.accepting_states.remove(state)

    def get_transition_type(
        self, from_state: State, symbol: str
    ) -> TransitionType | None:
        """Get the transition type for a given state and symbol

        Args:
            from_state: Source state
            symbol: Input symbol

        Returns:
            Optional[TransitionType]: Transition type if transition exists, None otherwise
        """
        if from_state not in self.transition_types:
            return None
        return self.transition_types[from_state].get(symbol)

    def is_accepting_state(self, state: State) -> bool:
        """Checks if a state is part of accepting state.
        Args:
            state(State): state to be checked.
        """
        if self.states is None or state < 0 or state > self.states:
            raise ValueError(f"State {state} does not exist")
        return state in self.accepting_states

    def has_transition(self, current_state: State, symbol: str) -> bool:
        """Checks if there is a transition for a symbol at a given state.
        Args:
            current_state(State): The state
            symbol(str): The symbol
        Returns:
            True when there is such a transition.
        """
        return self.transition(current_state, symbol) is not None

    def transition(self, current_state: State, symbol: str) -> State | None:
        """Get the next state based on current state and input symbol.

        Args:
            current_state: Current state
            symbol: Input symbol

        Returns:
            Optional[State]: Next state if transition exists, None otherwise
        """
        if current_state not in self.transitions:
            return None
        return self.transitions[current_state].get(symbol)

    def n_states(self):
        """Gets number of states.
        Returns:
            Number of states in the DFA.
        """
        return self.states + 1 if self.states is not None else 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DFA":
        """Create a DFA from a dictionary representation.

        Args:
            data: Dictionary representation of a DFA

        Returns:
            DFA: Reconstructed DFA object
        """
        # Create a new DFA with the alphabets
        dfa = cls(set(data["alphabets"]))

        # Restore states
        dfa.states = data["states"]

        # Restore transitions
        for state_str, transitions in data["transitions"].items():
            state = int(state_str)
            dfa.transitions[state] = {
                symbol: int(to_state) for symbol, to_state in transitions.items()
            }

        # Restore transition types
        for state_str, transitions in data["transition_types"].items():
            state = int(state_str)
            dfa.transition_types[state] = {
                symbol: TransitionType(type_value)
                for symbol, type_value in transitions.items()
            }

        # Restore initial state
        dfa.initial_state = data["initial_state"]

        # Restore accepting states
        dfa.accepting_states = set(data["accepting_states"])

        return dfa

    def to_dict(self) -> dict[str, Any]:
        """Serialize the DFA to a dictionary that can be converted to JSON.

        Returns:
            dict[str, Any]: Dictionary representation of the DFA
        """
        # Convert transition_types to a serializable format
        serializable_transition_types = {}
        for state, transitions in self.transition_types.items():
            serializable_transition_types[str(state)] = {
                symbol: trans_type.value for symbol, trans_type in transitions.items()
            }

        return {
            "states": self.states,
            "alphabets": list(self.alphabets),
            "transitions": {str(k): v for k, v in self.transitions.items()},
            "transition_types": serializable_transition_types,
            "initial_state": self.initial_state,
            "accepting_states": list(self.accepting_states),
        }
