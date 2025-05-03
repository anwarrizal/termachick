"""Unit tests for the Knuth-Morris-Pratt string matching algorithm.

This module contains test cases that verify the functionality of the KMPMatcher class,
including pattern matching with various inputs, edge cases, and both precomputed and
on-the-fly transition computation modes.
"""

import unittest
from strings.kmp import KMPMatcher


class TestKMPMatcher(unittest.TestCase):
    """KMPMatcher unit tests."""

    def test_basic_pattern_matching(self):
        """Test basic pattern matching."""
        # Test with precomputed transitions
        matcher = KMPMatcher("ABC", compute_transitions=True)
        self.assertEqual(list(matcher.search("ABCABCABC")), [(0, "ABC"), (3, "ABC"), (6,"ABC")])

        # Test with failure functions
        matcher = KMPMatcher("ABC", compute_transitions=False)
        self.assertEqual(list(matcher.search("ABCABCABC")), [(0, "ABC"), (3, "ABC"), (6, "ABC")])

    def test_empty_pattern(self):
        """Test that empty pattern raises error."""
        with self.assertRaises(ValueError):
            KMPMatcher("", compute_transitions=True)

    def test_empty_text(self):
        """Test that empty text matches the pattern."""
        matcher = KMPMatcher("ABC", compute_transitions=True)
        self.assertEqual(list(matcher.search("")), [])

    def test_pattern_not_found(self):
        """Tests the case when the pattern is not found in the string."""
        matcher = KMPMatcher("XYZ", alphabets="XYZABC", compute_transitions=True)
        self.assertEqual(list(matcher.search("ABCABCABC")), [])

    def test_overlapping_patterns(self):
        """Test that overlapping patterns are found."""
        matcher = KMPMatcher("ABC", compute_transitions=True)
        self.assertEqual(list(matcher.search("ABCABCABC")), [(0, "ABC"), (3, "ABC"), (6,"ABC")])
        # Test pattern that can overlap with itself
        matcher = KMPMatcher("AAAA", compute_transitions=True)
        self.assertEqual(list(matcher.search("AAAAAA")), [(0,"AAAA"), (1,"AAAA"), (2,"AAAA")])

    def test_single_character_pattern(self):
        """Test single character pattern."""
        matcher = KMPMatcher("A", alphabets="ACTG", compute_transitions=True)
        self.assertEqual(list(matcher.search("CTAGTTC")), [(2, "A")])

    def test_pattern_longer_than_text(self):
        """Test pattern longer than text."""
        matcher = KMPMatcher("ACGT", compute_transitions=True)
        self.assertEqual(list(matcher.search("GC")), [])

    def test_multiple_matches_with_failure_function(self):
        """Test specifically with failure function approach"""
        matcher = KMPMatcher("ACA", alphabets="ACGT", compute_transitions=False)
        self.assertEqual(list(matcher.search("ACACAGGACAGT")), [(0, "ACA"), (2, "ACA"), (7, "ACA")])

    def test_pattern_at_end(self):
        """Test pattern at the end of the text."""
        matcher = KMPMatcher("XYZ", alphabets="ABCXYZ", compute_transitions=True)
        self.assertEqual(list(matcher.search("ABCXYZ")), [(3, "XYZ")])

    def test_repeated_pattern(self):
        """Test repeated pattern."""
        matcher = KMPMatcher("AA", compute_transitions=True)
        self.assertEqual(list(matcher.search("AAAA")), [(0,"AA"), (1,"AA"), (2,"AA")])
