"""
Tests for filters.py - keyword and region filtering logic.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import config

# Override keywords/regions for isolated testing
config.KEYWORDS = [
    "machine learning", "psychology", "sociology", "computer science", "NLP"
]
config.REGIONS = []  # start with no region filter

from filters import matches_keywords, matches_region, is_relevant


class TestMatchesKeywords:
    def test_match_exact(self):
        assert matches_keywords("Postdoc in machine learning") is True

    def test_match_case_insensitive(self):
        assert matches_keywords("Postdoc in Machine Learning") is True
        assert matches_keywords("PSYCHOLOGY researcher") is True

    def test_no_match(self):
        assert matches_keywords("Postdoc in Chemistry") is False

    def test_partial_keyword_match(self):
        # "NLP" is in keywords, "NLP-based" should match
        assert matches_keywords("NLP-based postdoc position") is True

    def test_empty_keywords_matches_all(self):
        config.KEYWORDS = []
        assert matches_keywords("Anything at all") is True
        # Restore
        config.KEYWORDS = ["machine learning", "psychology", "sociology", "computer science", "NLP"]

    def test_multiple_keywords_any_match(self):
        assert matches_keywords("sociology and psychology research") is True


class TestMatchesRegion:
    def test_empty_regions_always_true(self):
        config.REGIONS = []
        assert matches_region("Some university in Japan") is True

    def test_region_match(self):
        config.REGIONS = ["USA", "UK"]
        assert matches_region("Harvard University, USA") is True
        assert matches_region("Oxford University, UK") is True

    def test_region_no_match(self):
        config.REGIONS = ["USA", "UK"]
        assert matches_region("University of Tokyo, Japan") is False

    def test_region_case_insensitive(self):
        config.REGIONS = ["USA"]
        assert matches_region("Some Lab usa") is True

    def teardown_method(self):
        config.REGIONS = []


class TestIsRelevant:
    def setup_method(self):
        config.KEYWORDS = ["machine learning", "psychology", "sociology"]
        config.REGIONS = []

    def test_relevant_by_title(self):
        assert is_relevant("Postdoc in Machine Learning") is True

    def test_relevant_by_description(self):
        assert is_relevant("Research Position", description="work involves psychology experiments") is True

    def test_not_relevant(self):
        assert is_relevant("Postdoc in Marine Biology", description="coral reef research") is False

    def test_relevant_location_not_used_for_keywords(self):
        # location is only used for region matching, not keyword matching
        assert is_relevant("Postdoc in Chemistry", location="machine learning lab") is False

    def test_relevant_with_region_filter(self):
        config.REGIONS = ["USA"]
        assert is_relevant("Postdoc in Psychology", location="Boston, USA") is True
        assert is_relevant("Postdoc in Psychology", location="Berlin, Germany") is False

    def teardown_method(self):
        config.REGIONS = []
