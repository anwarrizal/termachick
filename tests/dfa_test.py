
"""Module containing unit tests for the DFA class."""

import unittest
import json
import tempfile
from collections import deque
from enum import Enum

from strings.dfa import DFA, TransitionType, State


class TestDFA(unittest.TestCase):
    """Unit tests for the DFA class."""

    def setUp(self):
        """Set up test fixtures."""
        self.alphabets = set("abc")
        self.dfa = DFA(self.alphabets)

    def test_init(self):
        """Test DFA initialization."""
        self.assertEqual(self.dfa.alphabets, set("abc"))
        self.assertIsNone(self.dfa.states)
        self.assertEqual(self.dfa.transitions, {})
        self.assertEqual(self.dfa.transition_types, {})
        self.assertIsNone(self.dfa.initial_state)
        self.assertEqual(self.dfa.accepting_states, set())

    def test_add_state(self):
        """Test adding states to the DFA."""
        # Add a regular state
        state1 = self.dfa.add_state()
        self.assertEqual(state1, 0)
        self.assertEqual(self.dfa.states, 0)
        self.assertNotIn(state1, self.dfa.accepting_states)
        self.assertIsNone(self.dfa.initial_state)

        # Add an accepting state
        state2 = self.dfa.add_state(is_accepting=True)
        self.assertEqual(state2, 1)
        self.assertEqual(self.dfa.states, 1)
        self.assertIn(state2, self.dfa.accepting_states)

        # Add an initial state
        state3 = self.dfa.add_state(is_initial=True)
        self.assertEqual(state3, 2)
        self.assertEqual(self.dfa.states, 2)
        self.assertEqual(self.dfa.initial_state, state3)

        # Add an accepting and initial state
        state4 = self.dfa.add_state(is_accepting=True, is_initial=False)
        self.assertEqual(state4, 3)
        self.assertEqual(self.dfa.states, 3)
        self.assertIn(state4, self.dfa.accepting_states)

        # Try to add another initial state (should raise ValueError)
        with self.assertRaises(ValueError):
            self.dfa.add_state(is_initial=True)

    def test_add_transition(self):
        """Test adding transitions between states."""
        # Add states
        state0 = self.dfa.add_state(is_initial=True)
        state1 = self.dfa.add_state()
        state2 = self.dfa.add_state(is_accepting=True)

        # Add transitions
        self.dfa.add_transition(state0, "a", state1)
        self.dfa.add_transition(state1, "b", state2)
        self.dfa.add_transition(state0, "c", state0)  # Self-loop

        # Check transitions
        self.assertEqual(self.dfa.transition(state0, "a"), state1)
        self.assertEqual(self.dfa.transition(state1, "b"), state2)
        self.assertEqual(self.dfa.transition(state0, "c"), state0)
        self.assertIsNone(self.dfa.transition(state0, "b"))
        self.assertIsNone(self.dfa.transition(state1, "a"))

        # Check transition types
        self.assertEqual(self.dfa.get_transition_type(state0, "a"), TransitionType.SUCCESS)
        self.assertEqual(self.dfa.get_transition_type(state1, "b"), TransitionType.SUCCESS)

        # Add a failure transition
        self.dfa.add_transition(state1, "c", state0, TransitionType.FAILURE)
        self.assertEqual(self.dfa.transition(state1, "c"), state0)
        self.assertEqual(self.dfa.get_transition_type(state1, "c"), TransitionType.FAILURE)

        # Test error cases
        with self.assertRaises(ValueError):
            self.dfa.add_transition(state0, "a", state2)  # Duplicate transition
        with self.assertRaises(ValueError):
            self.dfa.add_transition(state0, "d", state1)  # Invalid symbol
        with self.assertRaises(ValueError):
            self.dfa.add_transition(5, "a", state1)  # Invalid from_state
        with self.assertRaises(ValueError):
            self.dfa.add_transition(state0, "a", 5)  # Invalid to_state

    def test_accepting_states(self):
        """Test accepting state functionality."""
        # Add states
        state0 = self.dfa.add_state()
        state1 = self.dfa.add_state(is_accepting=True)
        state2 = self.dfa.add_state()

        # Check accepting states
        self.assertFalse(self.dfa.is_accepting_state(state0))
        self.assertTrue(self.dfa.is_accepting_state(state1))
        self.assertFalse(self.dfa.is_accepting_state(state2))

        # Add another accepting state
        self.dfa.add_accepting(state0)
        self.assertTrue(self.dfa.is_accepting_state(state0))

        # Set accepting state
        self.dfa.set_accepting(state2, True)
        self.assertTrue(self.dfa.is_accepting_state(state2))
        self.dfa.set_accepting(state1, False)
        self.assertFalse(self.dfa.is_accepting_state(state1))

        # Test error cases
        with self.assertRaises(ValueError):
            self.dfa.is_accepting_state(5)  # Invalid state
        with self.assertRaises(ValueError):
            self.dfa.add_accepting(5)  # Invalid state

    def test_bfs_traverse(self):
        """Test BFS traversal of the DFA."""
        # Create a simple DFA
        state0 = self.dfa.add_state(is_initial=True)
        state1 = self.dfa.add_state()
        state2 = self.dfa.add_state(is_accepting=True)
        state3 = self.dfa.add_state()

        self.dfa.add_transition(state0, "a", state1)
        self.dfa.add_transition(state0, "b", state2)
        self.dfa.add_transition(state1, "c", state3)
        self.dfa.add_transition(state2, "a", state3)

        # Perform BFS traversal
        traversal = list(self.dfa.bfs_traverse())
        
        # Check traversal results
        self.assertEqual(len(traversal), 4)
        
        # Check that all transitions are included
        transitions = [(from_state, symbol, to_state) for from_state, symbol, to_state in traversal]
        self.assertIn((state0, "a", state1), transitions)
        self.assertIn((state0, "b", state2), transitions)
        
        # Test error case
        dfa_without_initial = DFA(set("abc"))
        with self.assertRaises(ValueError):
            list(dfa_without_initial.bfs_traverse())

    def test_has_transition(self):
        """Test has_transition method."""
        # Create a simple DFA
        state0 = self.dfa.add_state(is_initial=True)
        state1 = self.dfa.add_state()
        
        self.dfa.add_transition(state0, "a", state1)
        
        # Check has_transition
        self.assertTrue(self.dfa.has_transition(state0, "a"))
        self.assertFalse(self.dfa.has_transition(state0, "b"))
        self.assertFalse(self.dfa.has_transition(state1, "a"))

    def test_n_states(self):
        """Test n_states method."""
        # Empty DFA
        self.assertEqual(self.dfa.n_states(), 0)
        
        # Add states
        self.dfa.add_state()
        self.assertEqual(self.dfa.n_states(), 1)
        
        self.dfa.add_state()
        self.assertEqual(self.dfa.n_states(), 2)

    def test_serialization(self):
        """Test serialization and deserialization of DFA."""
        # Create a DFA with various features
        state0 = self.dfa.add_state(is_initial=True)
        state1 = self.dfa.add_state()
        state2 = self.dfa.add_state(is_accepting=True)
        
        self.dfa.add_transition(state0, "a", state1)
        self.dfa.add_transition(state1, "b", state2)
        self.dfa.add_transition(state0, "c", state0, TransitionType.FAILURE)
        
        # Convert to dictionary
        dfa_dict = self.dfa.to_dict()
        
        # Check dictionary structure
        self.assertEqual(dfa_dict["states"], 2)
        self.assertEqual(set(dfa_dict["alphabets"]), self.alphabets)
        self.assertEqual(dfa_dict["initial_state"], state0)
        self.assertEqual(dfa_dict["accepting_states"], [state2])
        
        # Deserialize back to DFA
        new_dfa = DFA.from_dict(dfa_dict)
        
        # Check deserialized DFA
        self.assertEqual(new_dfa.states, self.dfa.states)
        self.assertEqual(new_dfa.alphabets, self.dfa.alphabets)
        self.assertEqual(new_dfa.initial_state, self.dfa.initial_state)
        self.assertEqual(new_dfa.accepting_states, self.dfa.accepting_states)
        
        # Check transitions
        self.assertEqual(new_dfa.transition(state0, "a"), state1)
        self.assertEqual(new_dfa.transition(state1, "b"), state2)
        self.assertEqual(new_dfa.transition(state0, "c"), state0)
        
        # Check transition types
        self.assertEqual(new_dfa.get_transition_type(state0, "a"), TransitionType.SUCCESS)
        self.assertEqual(new_dfa.get_transition_type(state0, "c"), TransitionType.FAILURE)

    def test_to_json_and_from_json(self):
        """Test JSON serialization and deserialization."""
        # Create a simple DFA
        state0 = self.dfa.add_state(is_initial=True)
        state1 = self.dfa.add_state(is_accepting=True)
        self.dfa.add_transition(state0, "a", state1)
        
        # Convert to JSON
        dfa_json = json.dumps(self.dfa.to_dict())
        
        # Deserialize from JSON
        data = json.loads(dfa_json)
        new_dfa = DFA.from_dict(data)
        
        # Check deserialized DFA
        self.assertEqual(new_dfa.states, self.dfa.states)
        self.assertEqual(new_dfa.transition(state0, "a"), state1)
        self.assertTrue(new_dfa.is_accepting_state(state1))
