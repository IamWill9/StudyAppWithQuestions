# File: main.py
"""CLI entry for SC-200 Quiz App
- Auto-detects question JSON if --file not provided
- Adds --validate to check JSON structure and answer parsing
"""
import argparse
import glob
import os
import sys
from typing import List, Tuple

from quiz_app import load_questions, start_gui, normalize_mc_answer_to_letters


DEFAULT_CANDIDATES = [
    os.environ.get("SC200_JSON"),
    "questions/sc-200.json",
    "sc-200.json",
    "data/sc-200.json",
]


def find_default_json() -> str:
    for p in [p for p in DEFAULT_CANDIDATES if p]:
        if os.path.exists(p):
            return p
    # last resort: any sc-200.json in tree
    for p in glob.glob("**/sc-200.json", recursive=True):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        "Could not find a questions JSON. Pass --file or set SC200_JSON."
    )


def validate_questions(path: str) -> Tuple[int, List[str]]:
    topics = load_questions(path)
    issues: List[str] = []
    total = 0
    for topic, questions in topics.items():
        if not isinstance(questions, list):
            issues.append(f"Topic '{topic}' is not a list of questions")
            continue
        for idx, q in enumerate(questions, 1):
            total += 1
            # Basic fields
            if not isinstance(q, dict):
                issues.append(f"{topic}[{idx}] not an object")
                continue
            qtext = q.get("question")
            opts = q.get("options")
            ans = q.get("answer")
            qtype = q.get("type", "multiple_choice")

            if not qtext or not isinstance(qtext, str):
                issues.append(f"{topic}[{idx}] missing/invalid 'question'")
            if not isinstance(opts, list) or not opts:
                issues.append(f"{topic}[{idx}] missing/invalid 'options'")
                continue

            if qtype == "multiple_choice":
                letters = normalize_mc_answer_to_letters(opts, ans)
                if not letters:
                    issues.append(
                        f"{topic}[{idx}] MC answer unparseable; consider using letters like {list('ABCD')[:len(opts)]} or exact option text"
                    )
            elif qtype == "drag_and_drop":
                if not (isinstance(ans, list) and ans):
                    issues.append(f"{topic}[{idx}] DnD 'answer' must be a non-empty list")
            else:
                issues.append(f"{topic}[{idx}] unknown type '{qtype}'")

    return total, issues


def main():
    parser = argparse.ArgumentParser(description="Launch the SC-200 quiz app")
    parser.add_argument('--file', help='Path to question JSON file')
    parser.add_argument('--count', type=int, default=5, help='Number of questions to ask')
    parser.add_argument('--dark', action='store_true', help='Enable dark mode')
    parser.add_argument('--validate', action='store_true', help='Validate the questions JSON and exit')
    args = parser.parse_args()

    path = args.file or None
    if not path:
        try:
            path = find_default_json()
        except FileNotFoundError as e:
            print(str(e))
            sys.exit(2)

    if args.validate:
        total, issues = validate_questions(path)
        if issues:
            print(f"Validation FAILED: {len(issues)} issues found in {total} questions:\n")
            for i, msg in enumerate(issues, 1):
                print(f"{i:3d}. {msg}")
            sys.exit(1)
        else:
            print(f"Validation OK: {total} questions.")
            sys.exit(0)

    # Start GUI
    start_gui(path, args.count, dark_mode=args.dark)


if __name__ == '__main__':
    main()