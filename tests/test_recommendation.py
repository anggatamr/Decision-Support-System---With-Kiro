"""
Tests for utils/recommendation.py

Mencakup:
- Unit tests untuk collect_results, find_consensus, generate_report_text
- Property 32: find_consensus finds all tied best alternatives
"""

from __future__ import annotations

import pytest
from collections import Counter
from hypothesis import given, settings, strategies as st

from utils.recommendation import collect_results, find_consensus, generate_report_text


# ---------------------------------------------------------------------------
# Unit tests — collect_results
# ---------------------------------------------------------------------------

class TestCollectResults:
    def test_empty_session_state_returns_empty_dict(self):
        ss = {}
        result = collect_results(ss)
        assert result == {}

    def test_ev_results_only(self):
        ss = {
            "alt_names": ["A", "B", "C"],
            "ev_results": {
                "best_ev_idx": [1],
                "best_eol_idx": [0],
            },
        }
        result = collect_results(ss)
        assert result["EV"] == "B"
        assert result["EOL"] == "A"
        assert "Maximax" not in result

    def test_uncertainty_results_only(self):
        ss = {
            "alt_names": ["X", "Y"],
            "uncertainty_results": {
                "maximax_idx": [0],
                "maximin_idx": [1],
                "minimax_regret_idx": [0],
                "laplace_idx": [1],
            },
        }
        result = collect_results(ss)
        assert result["Maximax"] == "X"
        assert result["Maximin"] == "Y"
        assert result["Minimax Regret"] == "X"
        assert result["Laplace"] == "Y"
        assert "EV" not in result

    def test_all_results_present(self):
        ss = {
            "alt_names": ["Alt1", "Alt2", "Alt3"],
            "ev_results": {
                "best_ev_idx": [2],
                "best_eol_idx": [0],
            },
            "uncertainty_results": {
                "maximax_idx": [2],
                "maximin_idx": [1],
                "minimax_regret_idx": [2],
                "laplace_idx": [2],
            },
        }
        result = collect_results(ss)
        assert result["EV"] == "Alt3"
        assert result["EOL"] == "Alt1"
        assert result["Maximax"] == "Alt3"
        assert result["Maximin"] == "Alt2"
        assert result["Minimax Regret"] == "Alt3"
        assert result["Laplace"] == "Alt3"

    def test_no_ev_results_key(self):
        ss = {
            "alt_names": ["A", "B"],
            "ev_results": None,
        }
        result = collect_results(ss)
        assert "EV" not in result
        assert "EOL" not in result


# ---------------------------------------------------------------------------
# Unit tests — find_consensus
# ---------------------------------------------------------------------------

class TestFindConsensus:
    def test_single_winner(self):
        results = {"EV": "A", "EOL": "A", "Maximax": "B"}
        best, pct = find_consensus(results)
        assert best == ["A"]
        assert abs(pct - 200 / 3) < 1e-9

    def test_all_same(self):
        results = {"EV": "A", "EOL": "A", "Maximax": "A"}
        best, pct = find_consensus(results)
        assert best == ["A"]
        assert abs(pct - 100.0) < 1e-9

    def test_tie_two_alternatives(self):
        results = {"EV": "A", "EOL": "B", "Maximax": "A", "Maximin": "B"}
        best, pct = find_consensus(results)
        assert set(best) == {"A", "B"}
        assert abs(pct - 50.0) < 1e-9

    def test_single_method(self):
        results = {"EV": "Alpha"}
        best, pct = find_consensus(results)
        assert best == ["Alpha"]
        assert abs(pct - 100.0) < 1e-9

    def test_all_different(self):
        results = {"EV": "A", "EOL": "B", "Maximax": "C"}
        best, pct = find_consensus(results)
        # All tied at count=1
        assert set(best) == {"A", "B", "C"}
        assert abs(pct - 100 / 3) < 1e-9

    def test_three_way_tie_with_one_winner(self):
        results = {
            "EV": "A", "EOL": "A", "Maximax": "A",
            "Maximin": "B", "Minimax Regret": "C", "Laplace": "B",
        }
        best, pct = find_consensus(results)
        assert best == ["A"]
        assert abs(pct - 50.0) < 1e-9


# ---------------------------------------------------------------------------
# Unit tests — generate_report_text
# ---------------------------------------------------------------------------

class TestGenerateReportText:
    def test_contains_timestamp_marker(self):
        results = {"EV": "A", "EOL": "B"}
        consensus = ["A"]
        text = generate_report_text(results, consensus, 50.0)
        assert "Tanggal/Waktu Ekspor" in text

    def test_contains_all_methods(self):
        results = {"EV": "Alt1", "Maximax": "Alt2"}
        consensus = ["Alt1"]
        text = generate_report_text(results, consensus, 50.0)
        assert "EV" in text
        assert "Maximax" in text
        assert "Alt1" in text
        assert "Alt2" in text

    def test_contains_consensus_alternative(self):
        results = {"EV": "A", "EOL": "A", "Maximax": "B"}
        consensus = ["A"]
        text = generate_report_text(results, consensus, 66.7)
        assert "A" in text
        assert "66.7%" in text

    def test_tie_shows_all_alternatives(self):
        results = {"EV": "A", "EOL": "B"}
        consensus = ["A", "B"]
        text = generate_report_text(results, consensus, 50.0)
        assert "A" in text
        assert "B" in text
        assert "seri" in text.lower()

    def test_contains_disclaimer(self):
        results = {"EV": "A"}
        consensus = ["A"]
        text = generate_report_text(results, consensus, 100.0)
        assert "DISCLAIMER" in text.upper() or "disclaimer" in text.lower()

    def test_returns_string(self):
        results = {"EV": "A"}
        consensus = ["A"]
        text = generate_report_text(results, consensus, 100.0)
        assert isinstance(text, str)
        assert len(text) > 0


# ---------------------------------------------------------------------------
# Property 32: find_consensus finds all tied best alternatives
# **Validates: Requirements 9.3, 9.6**
# ---------------------------------------------------------------------------

# Strategy: generate a non-empty dict mapping method names to alternative names
method_names_st = st.lists(
    st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" "),
        min_size=1,
        max_size=20,
    ),
    min_size=1,
    max_size=10,
    unique=True,
)

alt_names_st = st.lists(
    st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), whitelist_characters=" "),
        min_size=1,
        max_size=20,
    ),
    min_size=1,
    max_size=5,
    unique=True,
)


@settings(max_examples=100)
@given(
    methods=method_names_st,
    alts=alt_names_st,
    data=st.data(),
)
def test_property_32_find_consensus_all_tied_best(methods, alts, data):
    """
    Property 32: find_consensus finds all tied best alternatives.

    For any dict mapping method names to alternative names,
    find_consensus(results) should:
    1. Return ALL alternatives tied for the highest frequency count.
    2. Return consensus percentage == max_count / len(results) * 100.

    **Validates: Requirements 9.3, 9.6**
    """
    # Build a results dict by sampling an alternative for each method
    results = {
        method: data.draw(st.sampled_from(alts))
        for method in methods
    }

    best, pct = find_consensus(results)

    # --- Verify the returned alternatives are exactly the tied best ---
    counts = Counter(results.values())
    max_count = max(counts.values())
    expected_best = {alt for alt, cnt in counts.items() if cnt == max_count}

    # All returned alternatives must be tied for max
    assert set(best) == expected_best, (
        f"Expected tied best {expected_best}, got {set(best)}"
    )

    # No duplicates in the returned list
    assert len(best) == len(set(best)), "find_consensus returned duplicate alternatives"

    # --- Verify the consensus percentage ---
    expected_pct = max_count / len(results) * 100
    assert abs(pct - expected_pct) < 1e-9, (
        f"Expected pct={expected_pct:.6f}, got pct={pct:.6f}"
    )

    # --- Verify percentage is in valid range [0, 100] ---
    assert 0.0 < pct <= 100.0, f"Consensus percentage {pct} out of range (0, 100]"
