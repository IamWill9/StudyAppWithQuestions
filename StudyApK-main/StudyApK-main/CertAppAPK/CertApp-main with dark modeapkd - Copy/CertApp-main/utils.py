# File: utils.py
import os
import json
import re
from typing import Iterable, List, Set, Tuple
from kivy.resources import resource_find, resource_add_path


def get_storage_path(filename):
    """
    Returns the absolute path for app data storage, using Kivy's user_data_dir if available,
    or falling back to a 'storage/' subfolder for desktop use.
    """
    try:
        from kivy.app import App
        user_data_dir = App.get_running_app().user_data_dir
        return os.path.join(user_data_dir, filename)
    except Exception:
        # fallback for desktop runs without Kivy App context
        return os.path.join('storage', filename)


def load_json(filepath):
    """
    Loads and parses JSON from a file. Supports:
    - Standard JSON arrays or dicts (topic->list). Dicts are flattened into one list.
    - Newline-separated JSON dicts (legacy/incorrect files).
    Returns a list of question objects (even if only one or none).
    """
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                flattened = []
                for value in data.values():
                    if isinstance(value, list):
                        flattened.extend(value)
                    else:
                        flattened.append(value)
                return flattened
            return data if isinstance(data, list) else [data]
        except Exception:
            # Handle legacy files with newline-separated dicts
            pattern = r'\{.*?\}(?=\s*\{|\s*$)'
            items = re.findall(pattern, content, flags=re.DOTALL)
            result = []
            for i, item in enumerate(items):
                try:
                    result.append(json.loads(item))
                except Exception as e:
                    print(f"Error parsing JSON object #{i+1} in '{filepath}': {e}")
            return result


def save_json(filepath, data):
    """Saves a Python object as pretty-printed UTF-8 JSON. Creates dirs if needed."""
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


# ---------------------------
# Answer normalization helpers
# ---------------------------

def _letters_map(n: int):
    return {chr(65 + i): i for i in range(n)}  # {'A':0, 'B':1, ...}


def normalize_mc_answer_to_letters(options: List[str], answer: Iterable) -> Set[str]:
    """Normalize an answer spec to a set of letters, e.g., {'A','C'}.
    Accepts answers as letters (A/B/…), letter+punct ("A:"/"A."), or full option text.
    """
    if answer is None:
        return set()
    if not isinstance(answer, (list, tuple, set)):
        items = [answer]
    else:
        items = list(answer)

    letters: Set[str] = set()
    letter_to_index = _letters_map(len(options))
    option_to_letter = {str(opt).strip(): chr(65 + i) for i, opt in enumerate(options)}

    for raw in items:
        s = str(raw).strip()
        if not s:
            continue
        # Case 1: starts with a letter (A/B/…) possibly followed by ':' or '.'
        first = s[0].upper()
        if first in letter_to_index:
            letters.add(first)
            continue
        # Case 2: exact option text
        if s in option_to_letter:
            letters.add(option_to_letter[s])
            continue
        # Case 3: token like "A:" or "A." at start
        token = s.split()[0].rstrip('.:').upper()
        if token in letter_to_index:
            letters.add(token)
            continue
    return letters


def format_correct_answer(options: List[str], letters_set: Set[str]) -> str:
    if not letters_set:
        return "Unknown"
    parts = []
    for L in sorted(letters_set):
        idx = ord(L) - 65
        if 0 <= idx < len(options):
            parts.append(f"{L}. {options[idx]}")
        else:
            parts.append(L)
    return ", ".join(parts)


def is_mc_selection_correct(options: List[str], correct, selected_letters: Set[str]) -> Tuple[bool, str]:
    """Return (is_correct, correct_display) for a user's letter selection vs. JSON answer."""
    correct_letters = normalize_mc_answer_to_letters(options, correct)
    if correct_letters:
        return selected_letters == correct_letters, format_correct_answer(options, correct_letters)

    # Fallback to comparing by option text if letters couldn't be parsed
    selected_texts = {options[ord(L) - 65] for L in selected_letters}
    correct_set = set(correct) if isinstance(correct, (list, tuple, set)) else {correct}
    is_ok = selected_texts == correct_set
    tmp_letters = normalize_mc_answer_to_letters(options, list(correct_set))
    display = format_correct_answer(options, tmp_letters) if tmp_letters else ", ".join(correct_set)
    return is_ok, display