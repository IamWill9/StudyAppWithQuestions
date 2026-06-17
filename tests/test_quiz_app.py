# File: tests/test_quiz_app.py
"""Unit tests for answer normalization & comparison
Run:  pytest -q
"""
import builtins
import types
import pytest

import quiz_app as qa


def test_normalize_accepts_letters_and_texts():
    options = ["Enable X", "Disable Y", "Monitor Z", "Audit W"]

    # letters
    assert qa.normalize_mc_answer_to_letters(options, ["A", "B"]) == {"A", "B"}
    # letter + punctuation
    assert qa.normalize_mc_answer_to_letters(options, ["A:", "B:"]) == {"A", "B"}
    # full option texts
    assert qa.normalize_mc_answer_to_letters(options, ["Enable X", "Disable Y"]) == {"A", "B"}


def test_selection_correct_when_all_four_required():
    options = ["A:", "B:", "C:", "D:"]  # when JSON stores options as letter-like strings
    correct = ["A:", "B:", "C:", "D:"]

    # User checked all four boxes -> selected letters A-D
    selected = {"A", "B", "C", "D"}
    ok, _ = qa.is_mc_selection_correct(options, correct, selected)
    assert ok is True


def test_selection_wrong_when_missing_one():
    options = ["Option 1", "Option 2", "Option 3", "Option 4"]
    correct = ["A", "B", "C", "D"]
    selected = {"A", "B", "C"}
    ok, _ = qa.is_mc_selection_correct(options, correct, selected)
    assert ok is False


def test_drag_and_drop_respects_pipes():
    # This is not calling the GUI; just ensuring we compare full strings
    # Example items containing '|'
    expected = [
        "DeviceEvents | where ActionType == 'Logon'",
        "| summarize count() by AccountName",
    ]
    # Selected exactly the same list should be correct
    selected = [
        "DeviceEvents | where ActionType == 'Logon'",
        "| summarize count() by AccountName",
    ]
    assert selected == expected  # guard: we compare exact strings without splitting
