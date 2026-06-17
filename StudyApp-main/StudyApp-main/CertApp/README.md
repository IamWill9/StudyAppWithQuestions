# CertApp (SC‑200 Quiz)

A Tkinter-based quiz app to practice for **Microsoft SC‑200** (Security Operations Analyst). It supports multiple‑choice and drag‑and‑drop questions, shows images, remembers what you’ve mastered, and keeps score history.

> ✅ This repository ships with a **test JSON question bank** (e.g., `sc-200.json`). The app’s parser accepts letters (A/B/…), letter+punctuation (e.g., `"A:"`), or full option texts.

---

## Features

- 🧠 Remembers correctly‑answered questions; serves missed ones first next time.
- ✅ Robust multiple‑choice parsing: letters, `A:`/`B.`, or full option text.
- 📎 Drag‑and‑drop uses exact string order (safe for KQL containing `|`).
- 🖼️ Inline images for questions and results.
- 📈 Score history with timestamps.
- 🌓 Optional dark theme.
- 🔍 JSON validator (`--validate`).

---

## Requirements

Install Python 3.9+ and create a virtual environment:

```bash
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

For development and tests, install the dev requirements instead:

```bash
python -m pip install -r requirements-dev.txt
```

> On Linux you may also need system Tk bindings:
>
> ```bash
> sudo apt-get install -y python3-tk python3-pil.imagetk
> ```

---

## Quick start

```bash
# Validate your questions JSON
python main.py --validate --file questions/sc-200.json

# Run the app (auto-detects JSON if not passed)
python main.py --count 10 --dark
```

**Windows PowerShell:**

```powershell
$env:SC200_JSON = "C:\\path\\to\\sc-200.json"
python .\main.py --count 10
```

**macOS/Linux (bash/zsh):**

```bash
export SC200_JSON="/path/to/sc-200.json"
python3 main.py --count 10
```

---

## JSON format (example)

```jsonc
{
  "KQL": [
    {
      "type": "multiple_choice",
      "question": "Which statements are true?",
      "options": ["Supports summarize", "Supports join", "Is case-sensitive", "Has let bindings"],
      "answer": ["A", "B", "D"],              // or ["A:"], or full option texts
      "explanation": "KQL supports summarize, join, and let; functions are case-insensitive by default.",
      "image": "Images/kql.png"
    },
    {
      "type": "drag_and_drop",
      "question": "Arrange the KQL steps in order:",
      "options": [
        "DeviceEvents | where ActionType == 'Logon'",
        "| summarize count() by AccountName",
        "| order by count_ desc"
      ],
      "answer": [
        "DeviceEvents | where ActionType == 'Logon'",
        "| summarize count() by AccountName",
        "| order by count_ desc"
      ],
      "explanation": "Filter → aggregate → order"
    }
  ]
}
```

### Multiple‑choice rules

- Provide **all** correct answers for multi‑select; the app compares sets of letters.
- Accepts `"A"`, `"A:"`, `"A."`, or full option text.

### Drag‑and‑drop rules

- `answer` must be a **list in the correct order**; compared as exact strings (pipes `|` are fine).

---

## File structure

```
.
├─ main.py                 # CLI: runs GUI, validates JSON
├─ quiz_app.py             # Tkinter app & parsing helpers
├─ requirements.txt        # runtime dependencies
├─ requirements-dev.txt    # test/development dependencies
├─ questions/
│  └─ sc-200.json          # test question bank
├─ Images/
│  ├─ meow.jpg             # pass image (score ≥ 79%)
│  └─ tryharder.jpg        # fail image
├─ data/                   # generated runtime memory/history; ignored by git
│  ├─ asked_questions.json
│  ├─ wrong_questions.json
│  └─ score_history.json
└─ tests/
   └─ test_quiz_app.py     # pytest: normalization & DnD checks
```

---

## Commands

```bash
python main.py [--file PATH] [--count N] [--dark] [--validate]
```

- `--file PATH`  : Path to your questions JSON. Omit to auto‑detect (or use env `SC200_JSON`).
- `--count N`    : Number of questions (default 5).
- `--dark`       : Enable dark mode.
- `--validate`   : Validate JSON and exit.

---

## Development

- Install dev dependencies: `python -m pip install -r requirements-dev.txt`
- Run tests: `python -m pytest -q`
- Style: PEP 8; small, testable helpers.

---

## Troubleshooting

- **ImportError for helpers**: `main.py` validates even if helper imports fail; make sure `quiz_app.py` is the updated version.
- **Images not showing**: check relative paths from the folder containing `main.py`/`quiz_app.py`.
- **Tkinter missing on Linux**: `sudo apt-get install python3-tk python3-pil.imagetk`.

---

## License / Use

Educational use only. You are responsible for question text/image rights. Do not distribute copyrighted question banks.

