# File: README.md (Kivy version)
# CertApp (Kivy / Mobile)

Kivy-based quiz app for practicing **Microsoft SC-200** on mobile (Buildozer/Android) or desktop. It supports multiple-choice questions, optional images, persistence of asked/correct questions, and a results history.

## Highlights
- ✅ **Answer parsing fixed**: accepts letters (e.g., `A`), letter+punctuation (`A:` or `A.`), **or** full option text. The UI displays options as `A. Option`, and compares **sets of letters** internally.
- 🧠 Remembers asked/correct questions and prioritizes missed ones next time.
- 🖼️ In-question images + result images.
- 📈 Score history with timestamps (see History screen).

## Run
```bash
pip install kivy pillow matplotlib
python main.py
```
Questions are loaded from `data/sc-200.json` (a dict of topics is also supported and flattened).

Best run in pydroid 

## Android (Buildozer)
- Ensure `buildozer.spec` includes Python 3, Kivy, Pillow, Matplotlib; add your `Images/` and `data/` resources.
- Use `resource_add_path`/`resource_find` to bundle images (already wired).

## JSON rules
- **Multiple-choice**: `answer` may be letters (e.g., `["A","C"]`), letter+punct (e.g., `["A:","C:"]`), or the full option texts. Provide **all** correct answers.
- **Yes/No multi**: if options are just `Yes`/`No` and multiple are expected, the screen shows indexed Yes/No groups and compares positions.

## Non-Commercial License (summary)
Use, modify, and share for **non-commercial** purposes only. Include attribution and this notice in distributions. See the main README for the full text.