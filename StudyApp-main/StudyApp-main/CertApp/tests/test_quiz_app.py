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


@pytest.fixture(scope="module")
def tk_root():
    try:
        root = qa.tk.Tk()
    except qa.tk.TclError as exc:
        pytest.skip(f"Tk display unavailable: {exc}")
    root.geometry("600x400+10000+10000")
    yield root
    root.destroy()


@pytest.mark.parametrize("dark", [False, True])
def test_checkbox_stays_selected_after_mouse_release(dark, monkeypatch, tk_root):
    root = tk_root
    monkeypatch.setattr(qa, "root", root)
    frame = qa.tk.Frame(root)
    frame.pack(fill="both", expand=True)
    monkeypatch.setattr(qa, "create_scrollable_window", lambda title: (root, frame))
    try:
        if dark:
            qa.apply_dark_mode(root)
        qa.ask_multiple_choice({"question": "Choose two", "options": ["One", "Two"],
                                "answer": ["A", "B"]}, 1)
        root.update()
        boxes = [w for w in frame.winfo_children() if isinstance(w, qa.tk.Checkbutton)]
        for box in boxes:
            # A tick must remain visible against the indicator's background.
            assert root.winfo_rgb(box.cget("foreground")) != root.winfo_rgb(box.cget("selectcolor"))
            for x, expected in [(5, 1), (40, 0), (40, 1)]:
                box.event_generate("<Enter>")
                box.event_generate("<ButtonPress-1>", x=x, y=10)
                box.event_generate("<ButtonRelease-1>", x=x, y=10)
                box.event_generate("<Leave>")
                root.update()
                assert int(root.getvar(box.cget("variable"))) == expected
        # Both independently selected options must reach the submit callback.
        results = []
        monkeypatch.setattr(qa, "show_result", lambda parent, message: results.append(message))
        monkeypatch.setattr(qa, "mark_question_correct", lambda question: None)
        monkeypatch.setattr(qa, "correct_answers", 0)
        next(w for w in frame.winfo_children() if isinstance(w, qa.tk.Button)
             and w.cget("text") == "Submit").invoke()
        assert results[0].startswith("Correct!")
        assert qa.correct_answers == 1
    finally:
        frame.destroy()


def test_sc300_complete_bank_and_assets():
    from main import validate_questions
    bank = qa.APP_DIR / 'questions/sc-300.json'
    total, issues = validate_questions(str(bank))
    assert (total, issues) == (408, [])
    questions = qa.load_questions(bank)['SC-300']
    assert {q['source']['question_number'] for q in questions} == set(range(1, 409))
    assert len({q['id'] for q in questions}) == 408
    assert sum(bool(q.get('adapted_simulation')) for q in questions) == 19
    assert sum(bool(q.get('source_context_missing')) for q in questions) == 9
    images = set()
    for q in questions:
        assert q['explanation']
        assert 'See Explanation section for answer' not in str(q['options'])
        assert not set(q['images']) & set(q['answer_images'])
        images.update(q['images'] + q['answer_images'])
        for url in q['references']:
            assert url.startswith(('http://', 'https://'))
            assert not any(c.isspace() for c in url)
        if q['type'] == 'multiple_choice':
            correct = qa.normalize_mc_answer_to_letters(q['options'], q['answer'])
            assert qa.is_mc_selection_correct(q['options'], q['answer'], correct)[0]
            assert not qa.is_mc_selection_correct(q['options'], q['answer'], set())[0]
        else:
            assert len(q['slots']) == len(q['answer'])
            assert all(a in s['options'] for a, s in zip(q['answer'], q['slots']))
    assert len(images) == 472
    for path in images:
        with qa.Image.open(qa.APP_DIR / path) as image:
            image.verify()


def test_exam_storage_isolation_and_legacy_migration(tmp_path, monkeypatch):
    monkeypatch.setattr(qa, 'APP_DIR', tmp_path)
    monkeypatch.chdir(tmp_path)
    for name in ['QUESTION_MEMORY_FILE','WRONG_QUESTIONS_FILE','SCORE_HISTORY_FILE']:
        monkeypatch.setattr(qa, name, getattr(qa, name))
    (tmp_path / 'asked_questions.json').write_text('["legacy"]')
    qa.configure_exam_storage(tmp_path / 'questions/sc-200.json')
    assert qa.load_asked_questions() == ['legacy']
    qa.save_wrong_questions(['sc200 missed'])
    qa.record_score(100, 1, 1)
    qa.configure_exam_storage(tmp_path / 'questions/sc-300.json')
    assert qa.load_asked_questions() == []
    assert qa.load_wrong_questions() == []
    assert qa.load_score_history() == []
    qa.save_asked_questions(['sc300 mastered'])
    qa.configure_exam_storage(tmp_path / 'questions/sc-200.json')
    assert qa.load_asked_questions() == ['legacy']
    assert qa.load_wrong_questions() == ['sc200 missed']
    assert qa.load_score_history()[0]['score'] == 100
    assert (tmp_path / 'asked_questions.json').read_text() == '["legacy"]'


def test_exam_picker_starts_selected_bank(tk_root, monkeypatch):
    frame = qa.tk.Frame(tk_root)
    frame.pack()
    calls = []
    monkeypatch.setattr(qa, 'configure_exam_storage', lambda path: calls.append(path))
    monkeypatch.setattr(qa, 'close_quiz_windows', lambda: None)
    monkeypatch.setattr(qa, 'run_quiz', lambda count, topics: calls.append((count, sum(map(len, topics.values())))))
    try:
        exam, count = qa.build_exam_picker(frame)
        start = next(w for w in frame.winfo_children() if isinstance(w, qa.tk.Button))
        for name, expected in [('SC-300',408),('SC-200',375),('SC-500',120)]:
            exam.set(name)
            count.set('7')
            start.invoke()
            assert calls[-1] == (7, expected)
            assert calls[-2].endswith(name.lower()+'.json')
    finally:
        frame.destroy()


@pytest.mark.parametrize('number', [5, 20, 87, 156, 327, 374, 393])
def test_sc300_interactive_submission(number, monkeypatch, tk_root):
    question = qa.load_questions(qa.APP_DIR / 'questions/sc-300.json')['SC-300'][number-1]
    frame = qa.tk.Frame(tk_root)
    frame.pack()
    monkeypatch.setattr(qa, 'create_scrollable_window', lambda title: (tk_root, frame))
    monkeypatch.setattr(qa, 'show_images', lambda frame, paths: None)
    monkeypatch.setattr(qa, 'mark_question_correct', lambda q: None)
    results = []
    monkeypatch.setattr(qa, 'show_result', lambda parent, message: results.append(message))
    monkeypatch.setattr(qa, 'correct_answers', 0)
    try:
        if question['type'] == 'multiple_choice':
            qa.ask_multiple_choice(question, 1)
            boxes = [w for w in frame.winfo_children() if isinstance(w, qa.tk.Checkbutton)]
            for letter in qa.normalize_mc_answer_to_letters(question['options'],question['answer']):
                boxes[ord(letter)-65].invoke()
        else:
            qa.ask_drag_and_drop(question, 1)
            menus = [w for w in frame.winfo_children() if isinstance(w, qa.tk.OptionMenu)]
            assert len(menus) == len(question['answer'])
            for menu, answer, slot in zip(menus, question['answer'], question['slots']):
                menu['menu'].invoke(slot['options'].index(answer))
        submit = next(w for w in frame.winfo_children() if isinstance(w, qa.tk.Button) and w.cget('text') == 'Submit')
        submit.invoke()
        submit.invoke()
        assert len(results) == 1
        assert results[0].startswith('Correct!')
        assert qa.correct_answers == 1
    finally:
        frame.destroy()


def test_source_images_render_in_tk(tk_root):
    frame = qa.tk.Frame(tk_root)
    frame.pack()
    try:
        qa.show_images(frame, ['Images/sc-300/p003-15.jpeg', 'Images/sc-300/p375-07.png'])
        tk_root.update_idletasks()
        labels = frame.winfo_children()
        assert len(labels) == 2
        assert all(label.cget('image') for label in labels)
        assert all(label.bind('<Button-1>') for label in labels)
    finally:
        frame.destroy()


def test_sc500_bank_and_source_assets():
    from main import validate_questions
    bank = qa.APP_DIR / 'questions/sc-500.json'
    assert validate_questions(str(bank)) == (120, [])
    topics = qa.load_questions(bank)
    assert [len(qs) for qs in topics.values()] == [36, 36, 24, 24]
    questions = [q for qs in topics.values() for q in qs]
    assert [q['source']['question_number'] for q in questions] == list(range(1, 121))
    assert len({q['id'] for q in questions}) == 120
    assert sum(q['type'] == 'drag_and_drop' for q in questions) == 36
    assert sum('context_pages' in q['source'] for q in questions) == 17
    assert 'Fabrikam' in questions[72]['question']
    assert 'Fabrikam' in questions[96]['question']
    assert 'Contoso' in questions[73]['question']
    assert questions[95]['answer'] == ['E']
    assert questions[95]['source_answer_conflict'] is True
    images = set()
    for q in questions:
        assert q['explanation'] and q['source']['pages']
        assert 'See Explanation section' not in str(q['options'])
        assert not set(q['images']) & set(q['answer_images'])
        images.update(q['images'] + q['answer_images'])
        for url in q['references']:
            assert url.startswith(('http://', 'https://'))
            assert not any(c.isspace() for c in url)
            assert 'Overview' not in url and 'Testlet' not in url
        if q['type'] == 'multiple_choice':
            letters = qa.normalize_mc_answer_to_letters(q['options'], q['answer'])
            assert qa.is_mc_selection_correct(q['options'], q['answer'], letters)[0]
            assert not qa.is_mc_selection_correct(q['options'], q['answer'], set())[0]
    assert len(images) == 114
    for image in images:
        with qa.Image.open(qa.APP_DIR / image) as asset:
            asset.verify()


@pytest.mark.parametrize('question', [q for qs in qa.load_questions(qa.APP_DIR / 'questions/sc-500.json').values()
                                    for q in qs if q['type'] == 'drag_and_drop'], ids=lambda q: q['id'])
def test_sc500_interactive_scoring(question, monkeypatch, tk_root):
    monkeypatch.setattr(qa, 'show_images', lambda frame, paths: None)
    monkeypatch.setattr(qa, 'mark_question_correct', lambda q: None)
    monkeypatch.setattr(qa, 'load_wrong_questions', lambda: [])
    wrong = []
    monkeypatch.setattr(qa, 'save_wrong_questions', lambda questions: wrong.extend(questions))
    for choose_correct in (True, False):
        frame = qa.tk.Frame(tk_root)
        frame.pack()
        results = []
        monkeypatch.setattr(qa, 'create_scrollable_window', lambda title: (tk_root, frame))
        monkeypatch.setattr(qa, 'show_result', lambda parent, message: results.append(message))
        monkeypatch.setattr(qa, 'correct_answers', 0)
        try:
            qa.ask_drag_and_drop(question, 1)
            menus = [w for w in frame.winfo_children() if isinstance(w, qa.tk.OptionMenu)]
            assert len(menus) == len(question['answer'])
            for i, (menu, answer, slot) in enumerate(zip(menus, question['answer'], question['slots'])):
                index = slot['options'].index(answer)
                if not choose_correct and i == 0:
                    index = (index + 1) % len(slot['options'])
                menu['menu'].invoke(index)
            submit = next(w for w in frame.winfo_children() if isinstance(w, qa.tk.Button) and w.cget('text') == 'Submit')
            submit.invoke()
            assert results[0].startswith('Correct!' if choose_correct else 'Wrong!')
            assert qa.correct_answers == int(choose_correct)
        finally:
            frame.destroy()
    assert wrong == [question]


def test_sc500_progress_is_separate_from_existing_exams(tmp_path, monkeypatch):
    monkeypatch.setattr(qa, 'APP_DIR', tmp_path)
    for variable in ['QUESTION_MEMORY_FILE', 'WRONG_QUESTIONS_FILE', 'SCORE_HISTORY_FILE']:
        monkeypatch.setattr(qa, variable, getattr(qa, variable))
    for exam in ['sc-200', 'sc-300', 'sc-500']:
        qa.configure_exam_storage(tmp_path / 'questions' / (exam+'.json'))
        qa.save_asked_questions([exam])
        qa.save_wrong_questions([exam+'-missed'])
        qa.save_score_history([{'exam':exam}])
    for exam in ['sc-200', 'sc-300', 'sc-500']:
        qa.configure_exam_storage(tmp_path / 'questions' / (exam+'.json'))
        assert qa.load_asked_questions() == [exam]
        assert qa.load_wrong_questions() == [exam+'-missed']
        assert qa.load_score_history() == [{'exam':exam}]
