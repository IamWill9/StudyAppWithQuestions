# StudytApp (SC-200 Quiz, Kivy Version)

[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)  
[![Kivy](https://img.shields.io/badge/Kivy-2.3-green.svg)](https://kivy.org/)  
[![License: NC](https://img.shields.io/badge/license-Non--Commercial-orange.svg)](#license--use)

A **Kivy-based quiz app** for practicing **Microsoft SC-200** (Security Operations Analyst) on **mobile (Android via Buildozer)** or desktop.  
It supports multiple-choice questions, optional images, persistence of asked/correct questions, and a results history.

> ✅ This repository ships with a **test JSON question bank** (e.g., `data/yourfile.json`).  
> The parser accepts answers as letters (`A`/`B`…), letter+punctuation (`"A:"`, `"A."`), or full option texts.

---

## Highlights

- ✅ Robust multiple-choice parsing: letters, `A:`/`A.`, or full option text. UI displays `A. Option`, comparisons done internally on sets of letters.
- 🧠 Remembers asked/correct questions; prioritizes missed ones next time.
- 🖼️ Supports inline question images and result images.
- 📈 Score history with timestamps (see **History** screen).

---

## Requirements

Install Python 3.9+ and dependencies:

```bash
pip install kivy pillow matplotlib
```

---

## Quick start

```bash
# Run on desktop
python main.py
```

Questions are loaded from:

```
data/yourfile.json
```

A dict of topics is also supported and will be automatically flattened.

---

## Android (Buildozer)

- Ensure `buildozer.spec` includes:
  - Python 3
  - Kivy
  - Pillow
  - Matplotlib
- Add your `Images/` and `data/` resources.
- Use `resource_add_path` / `resource_find` to bundle images (already wired).

⚠️ **Note:** The APK build may encounter issues on some setups,  
but the app runs fine on **Pydroid (Android)**.

---

## JSON format (rules)

### Multiple-choice

- Answers may be:
  - `["A", "C"]`
  - `["A:", "C:"]`
  - full option texts
- Provide **all correct answers** for multi-select questions.

### Yes/No (multi)

- If options are just `Yes` / `No` and multiple are expected:
  - The app shows indexed Yes/No groups.
  - Compares answers by **position**.

---

## File structure

```
.
├─ main.py                 # Entry point
├─ data/
│  └─ yourfile.json        # test question bank
├─ Images/                 # bundled images
├─ asked_questions.json    # generated at runtime
├─ wrong_questions.json    # generated at runtime
└─ score_history.json      # generated at runtime
```

---

## License / Use

**Non-Commercial License**  
- Use, modify, and share for **non-commercial purposes only**.  
- Include attribution and this notice in distributions.  
- See the main README for the full text.

---

## Philosophy

USE THE DUMPS TO TEST THE GAINED KNOWLEDGE.  
THE TRIALS BEFORE YOU ARE BUT MIRRORS OF YOUR LEARNING; FACE THEM, LEST YOU BETRAY YOUR OWN POTENTIAL.
