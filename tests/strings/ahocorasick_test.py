"""Unit tests for the Aho-Corasick string matching algorithm."""

import unittest
from strings.ahocorasick import AhoCorasickMatcher


class TestAhoCorasickMatcher(unittest.TestCase):
    """Unit tests for ahocorasick module."""

    def setUp(self):
        # Common setup that runs before each test
        self.simple_patterns = ["ABABAC", "ABAB"]
        self.alphabets = "ABC"

    def test_initialization(self):
        """Test basic initialization"""
        matcher = AhoCorasickMatcher(
            patterns=self.simple_patterns, compute_transitions=True
        )
        self.assertIsNotNone(matcher.dfa)
        self.assertIsNotNone(matcher.fail_functions)
        self.assertIsNotNone(matcher.pattern_map)

    def test_initialization_with_explicit_alphabet(self):
        """Test initialization with explicit alphabet"""
        matcher = AhoCorasickMatcher(
            patterns=self.simple_patterns,
            compute_transitions=True,
            alphabets=self.alphabets,
        )
        self.assertIsNotNone(matcher.dfa)

    def test_simple_pattern_match(self):
        """Test basic pattern matching"""
        matcher = AhoCorasickMatcher(
            patterns=["ABC"], alphabets="ABCDEF", compute_transitions=True
        )
        matches = list(matcher.search("AABCDEF"))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], (1, "ABC"))

    def test_overlapping_patterns(self):
        """Test matching overlapping patterns"""
        matcher = AhoCorasickMatcher(
            patterns=["ABBAB", "BABBA"], compute_transitions=True
        )
        matches = list(matcher.search("ABABBABBBA"))
        self.assertEqual(len(matches), 2)
        self.assertEqual(matches[0], (1, "BABBA"))
        self.assertEqual(matches[1], (2, "ABBAB"))

    def test_no_matches(self):
        """Test when no matches are found"""
        matcher = AhoCorasickMatcher(
            patterns=["XYZ"], alphabets="ABCDEFXYZ", compute_transitions=True
        )
        matches = list(matcher.search("ABCDEF"))
        self.assertEqual(len(matches), 0)

    def test_empty_text(self):
        """Test searching in empty text"""
        matcher = AhoCorasickMatcher(
            patterns=self.simple_patterns, compute_transitions=True
        )
        matches = list(matcher.search(""))
        self.assertEqual(len(matches), 0)

    def test_empty_patterns(self):
        """Test initialization with empty patterns list"""
        with self.assertRaises(ValueError):
            AhoCorasickMatcher(patterns=[], compute_transitions=True)

    def test_on_the_fly_computation(self):
        """Test matcher with compute_transitions=False"""
        matcher = AhoCorasickMatcher(
            patterns=self.simple_patterns, compute_transitions=False
        )
        matches = list(matcher.search("ABABAC"))
        self.assertEqual(len(matches), 2)  # Should find both "ABAB" and "ABABAC"

    def test_multiple_occurrences(self):
        """Test finding multiple occurrences of the same pattern"""
        matcher = AhoCorasickMatcher(patterns=["AB"], compute_transitions=True)
        matches = list(matcher.search("ABABAB"))
        self.assertEqual(len(matches), 3)
        expected_positions = [(0, "AB"), (2, "AB"), (4, "AB")]
        self.assertEqual(matches, expected_positions)

    def test_multiple_matches_with_failure_function(self):
        """Test specifically with failure function approach"""
        matcher = AhoCorasickMatcher(
            patterns=["ACA"], alphabets="ACGT", compute_transitions=False
        )
        self.assertEqual(
            list(matcher.search("ACACAGGACAGT")), [(0, "ACA"), (2, "ACA"), (7, "ACA")]
        )

    def test_pattern_at_end(self):
        """Test matching pattern at the end of text"""
        matcher = AhoCorasickMatcher(
            patterns=["ABC", "AXXA", "ABX"], alphabets="ABCX", compute_transitions=True
        )
        matches = list(matcher.search("XXXXABC"))
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], (4, "ABC"))
