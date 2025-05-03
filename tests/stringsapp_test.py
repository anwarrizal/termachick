import unittest
import json
import os
import sys
import tempfile
from unittest.mock import patch, mock_open, MagicMock

from strings.stringsapp import (
    read_input,
    build_dfa,
    load_matcher_from_file,
    search_with_patterns,
    search_with_dfa,
)
from strings.kmp import KMPMatcher
from strings.ahocorasick import AhoCorasickMatcher
from strings.dfa import DFA, TransitionType


class TestStringsApp(unittest.TestCase):
    """Unit tests for the stringsapp module."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_patterns = ["ABC", "DEF", "GHI"]
        self.test_text = "ABCDEFGHI"
        
        # Create a temporary directory for test files
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        
        # Create test files
        self.test_file_path = os.path.join(self.temp_dir.name, "test_input.txt")
        with open(self.test_file_path, "w", encoding="utf-8") as f:
            f.write(self.test_text)
            
        self.output_file_path = os.path.join(self.temp_dir.name, "test_dfa.json")

    def test_read_input_from_file(self):
        """Test reading input from a file."""
        result = read_input(self.test_file_path)
        self.assertEqual(result, self.test_text)

    @patch('sys.stdin.read')
    def test_read_input_from_stdin(self, mock_stdin_read):
        """Test reading input from stdin."""
        mock_stdin_read.return_value = self.test_text
        result = read_input(None)
        self.assertEqual(result, self.test_text)
        mock_stdin_read.assert_called_once()

    @patch('builtins.print')
    def test_build_dfa_kmp(self, mock_print):
        """Test building a KMP DFA."""
        # Build a KMP DFA
        build_dfa(
            patterns=[self.test_patterns[0]],
            output_file=self.output_file_path,
            algorithm="kmp",
            precompute=True
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_file_path))
        
        # Check the file contents
        with open(self.output_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data["algorithm"], "kmp")
        self.assertEqual(data["pattern"], self.test_patterns[0])
        self.assertIn("dfa", data)
        self.assertIn("fail_functions", data)
        
        # Check that the print message was called
        mock_print.assert_called_with(f"KMP DFA for pattern '{self.test_patterns[0]}' saved to {self.output_file_path}")

    @patch('builtins.print')
    def test_build_dfa_aho_corasick(self, mock_print):
        """Test building an Aho-Corasick DFA."""
        # Build an Aho-Corasick DFA
        build_dfa(
            patterns=self.test_patterns,
            output_file=self.output_file_path,
            algorithm="aho-corasick",
            precompute=True
        )
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_file_path))
        
        # Check the file contents
        with open(self.output_file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        self.assertEqual(data["algorithm"], "aho-corasick")
        self.assertEqual(data["patterns"], self.test_patterns)
        self.assertIn("dfa", data)
        self.assertIn("fail_functions", data)
        self.assertIn("pattern_map", data)
        
        # Check that the print message was called
        mock_print.assert_called_with(f"Aho-Corasick DFA for {len(self.test_patterns)} patterns saved to {self.output_file_path}")

    @patch('builtins.print')
    def test_build_dfa_kmp_multiple_patterns_warning(self, mock_print):
        """Test warning when using KMP with multiple patterns."""
        # Build a KMP DFA with multiple patterns
        build_dfa(
            patterns=self.test_patterns,
            output_file=self.output_file_path,
            algorithm="kmp",
            precompute=True
        )
        
        # Check that the warning was printed
        mock_print.assert_any_call("Warning: KMP only supports a single pattern. Using the first pattern.")

    def test_load_matcher_from_file_kmp(self):
        """Test loading a KMP matcher from a file."""
        # First build a KMP DFA
        build_dfa(
            patterns=[self.test_patterns[0]],
            output_file=self.output_file_path,
            algorithm="kmp",
            precompute=True
        )
        
        # Load the matcher
        matcher = load_matcher_from_file(self.output_file_path)
        
        # Check that it's a KMP matcher
        self.assertIsInstance(matcher, KMPMatcher)
        self.assertEqual(matcher.compute_transitions, True)
        self.assertIsNotNone(matcher.dfa)
        self.assertIsNotNone(matcher.fail_functions)

    def test_load_matcher_from_file_aho_corasick(self):
        """Test loading an Aho-Corasick matcher from a file."""
        # First build an Aho-Corasick DFA
        build_dfa(
            patterns=self.test_patterns,
            output_file=self.output_file_path,
            algorithm="aho-corasick",
            precompute=True
        )
        
        # Load the matcher
        matcher = load_matcher_from_file(self.output_file_path)
        
        # Check that it's an Aho-Corasick matcher
        self.assertIsInstance(matcher, AhoCorasickMatcher)
        self.assertEqual(matcher.compute_transitions, True)
        self.assertIsNotNone(matcher.dfa)
        self.assertIsNotNone(matcher.fail_functions)
        self.assertIsNotNone(matcher.pattern_map)

    def test_load_matcher_from_file_unknown_format(self):
        """Test loading a matcher from a file with unknown format."""
        # Create a minimal DFA file
        dfa = DFA(set("ABC"))
        state0 = dfa.add_state(is_initial=True)
        state1 = dfa.add_state(is_accepting=True)
        dfa.add_transition(state0, "A", state1)
        
        data = {
            "dfa": dfa.to_dict(),
            "pattern_map": {"1": "ABC"}  # This will make it guess Aho-Corasick
        }
        
        with open(self.output_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        # Load the matcher
        matcher = load_matcher_from_file(self.output_file_path)
        
        # Check that it guessed Aho-Corasick
        self.assertIsInstance(matcher, AhoCorasickMatcher)

    def test_load_matcher_from_file_unknown_format_kmp(self):
        """Test loading a matcher from a file with unknown format (KMP guess)."""
        # Create a minimal DFA file
        dfa = DFA(set("ABC"))
        state0 = dfa.add_state(is_initial=True)
        state1 = dfa.add_state(is_accepting=True)
        dfa.add_transition(state0, "A", state1)
        
        data = {
            "dfa": dfa.to_dict(),
            # No pattern_map, so it should guess KMP
        }
        
        with open(self.output_file_path, "w", encoding="utf-8") as f:
            json.dump(data, f)
        
        # Load the matcher
        matcher = load_matcher_from_file(self.output_file_path)
        
        # Check that it guessed KMP
        self.assertIsInstance(matcher, KMPMatcher)

    @patch('builtins.print')
    def test_search_with_patterns_kmp(self, mock_print):
        """Test searching with KMP."""
        # Search with KMP
        results = search_with_patterns(
            text=self.test_text,
            patterns=[self.test_patterns[0]],
            algorithm="kmp",
            precompute=True
        )
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], 0)  # "ABC" found at position 0

    @patch('builtins.print')
    def test_search_with_patterns_kmp_save_dfa(self, mock_print):
        """Test searching with KMP and saving the DFA."""
        # Search with KMP and save DFA
        results = search_with_patterns(
            text=self.test_text,
            patterns=[self.test_patterns[0]],
            algorithm="kmp",
            precompute=True,
            save_dfa=self.output_file_path
        )
        
        # Check results
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], 0)  # "ABC" found at position 0
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_file_path))
        
        # Check that the print message was called
        mock_print.assert_called_with(f"Saved KMP DFA to {self.output_file_path}")

    def test_search_with_patterns_aho_corasick(self):
        """Test searching with Aho-Corasick."""
        # Search with Aho-Corasick
        results = search_with_patterns(
            text=self.test_text,
            patterns=self.test_patterns,
            algorithm="aho-corasick",
            precompute=True
        )
        
        # Check results
        self.assertEqual(len(results), 3)
        expected_results = [(0, "ABC"), (3, "DEF"), (6, "GHI")]
        for result, expected in zip(results, expected_results):
            self.assertEqual(result, expected)

    @patch('builtins.print')
    def test_search_with_patterns_aho_corasick_save_dfa(self, mock_print):
        """Test searching with Aho-Corasick and saving the DFA."""
        # Search with Aho-Corasick and save DFA
        results = search_with_patterns(
            text=self.test_text,
            patterns=self.test_patterns,
            algorithm="aho-corasick",
            precompute=True,
            save_dfa=self.output_file_path
        )
        
        # Check results
        self.assertEqual(len(results), 3)
        
        # Check that the file was created
        self.assertTrue(os.path.exists(self.output_file_path))
        
        # Check that the print message was called
        mock_print.assert_called_with(f"Saved Aho-Corasick DFA to {self.output_file_path}")

    @patch('builtins.print')
    def test_search_with_dfa(self, mock_print):
        """Test searching with a pre-built DFA."""
        # First build an Aho-Corasick DFA
        build_dfa(
            patterns=self.test_patterns,
            output_file=self.output_file_path,
            algorithm="aho-corasick",
            precompute=True
        )
        
        # Search with the pre-built DFA
        results = search_with_dfa(
            text=self.test_text,
            dfa_file=self.output_file_path,
            precompute=True
        )
        
        # Check results
        self.assertEqual(len(results), 3)
        expected_results = [(0, "ABC"), (3, "DEF"), (6, "GHI")]
        for result, expected in zip(results, expected_results):
            self.assertEqual(result, expected)
        
        # Check that the print message was called
        mock_print.assert_called_with(f"Loaded DFA from {self.output_file_path}")

