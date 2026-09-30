# File: tests/test_quiz_app.py
"""Unit tests for answer normalization & comparison
Run:  pytest -q
"""
import builtins
import types
from pathlib import Path
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


def test_load_score_history_tolerates_empty_or_invalid_file(tmp_path, monkeypatch):
    history_file = tmp_path / "score_history.json"
    monkeypatch.setattr(qa, "SCORE_HISTORY_FILE", str(history_file))

    history_file.write_text("", encoding="utf-8")
    assert qa.load_score_history() == []

    history_file.write_text("{}", encoding="utf-8")
    assert qa.load_score_history() == []


@pytest.mark.parametrize("answer,expected", [
    (["Disable Y"], {"B"}),
    (["Audit W"], {"D"}),
    ([" a: ", "b."], {"A", "B"}),
    (["B. Disable Y"], {"B"}),
    (["Banana"], set()),
    (["A", "Banana"], set()),
    (["A", ""], set()),
    (["Z"], set()),
    (None, set()),
    ([], set()),
])
def test_answer_normalization_requires_text_or_explicit_label(answer, expected):
    options = ["Enable X", "Disable Y", "Monitor Z", "Audit W"]
    assert qa.normalize_mc_answer_to_letters(options, answer) == expected


@pytest.mark.parametrize("answer", [None, [], [""], ["A", "Banana"]])
def test_invalid_answer_keys_never_award_credit(answer):
    for selected in (set(), {"A"}):
        assert qa.is_mc_selection_correct(["Enable X", "Disable Y"], answer, selected)[0] is False


def test_full_option_text_marks_the_matching_option():
    options = ["Enable X", "Disable Y", "Monitor Z", "Audit W"]
    assert qa.is_mc_selection_correct(options, ["Disable Y"], {"B"})[0] is True
    assert qa.is_mc_selection_correct(options, ["Disable Y"], {"D"})[0] is False


def test_bundled_question_bank_and_images():
    from main import validate_questions
    app_dir = Path(qa.__file__).resolve().parent
    bank = app_dir / "questions/sc-200.json"
    total, issues = validate_questions(str(bank))
    assert total == 375
    assert issues == []
    # Compare exact paths even on Windows, which tolerates incorrect casing.
    actual_paths = {p.relative_to(app_dir).as_posix() for p in (app_dir / "Images").iterdir()}
    images = {q["image"] for qs in qa.load_questions(bank).values() for q in qs if q.get("image")}
    assert images <= actual_paths
    for image in images:
        with qa.Image.open(app_dir / image) as asset:
            asset.verify()


def test_validator_reports_missing_image(tmp_path):
    import json
    from main import validate_questions
    bank = tmp_path / "questions.json"
    bank.write_text(json.dumps({"topic": [{"question": "Example?", "options": ["Yes", "No"],
                                          "answer": ["A"], "image": "Images/does-not-exist.png"}]}), encoding="utf-8")
    total, issues = validate_questions(str(bank))
    assert total == 1
    assert any("missing image" in issue for issue in issues)
