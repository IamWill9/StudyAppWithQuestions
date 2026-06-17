# CertApp

This is a graphical quiz application designed to help users study and practice for InfoSec certification, currently limited to  Microsoft SC-200 (Microsoft Security Operations Analyst) exam questions. The application uses Python's `tkinter` library for the user interface and supports:

- Multiple-choice questions
- Image-based questions
- Persistent memory of previously asked questions

## Features

- 🧠 Tracks previously asked questions to avoid repetition.
- 📊 Displays quiz results and relevant images based on performance.
- 🎨 Image rendering within questions using `matplotlib` and `PIL`.
- 🗓️ Records score history with dates and displays it after each quiz.
- 🌙 Optional dark mode via the `--dark` launch flag.

## Prerequisites

Ensure the following Python libraries are installed:

```bash
pip install pillow matplotlib
```
## Usage

Run the application with:
```bash
python main.py --file questions/sc-200.json --count 5 [--dark]
```

Questions are loaded from the specified JSON file. Images should remain in the `Images/` directory.

## File Structure

- `quiz_app.py` — Core quiz logic.
- `main.py` — Launcher script that loads a question file.
- `questions/` — Folder containing JSON question sets.
- `asked_questions.json` — Memory of previously asked questions.
- `Images/` — Folder containing result and question-related images

## License

```
By contributing, you agree to the following:

Contributor Agreement
By participating in this project as a contributor, you acknowledge and agree to the following:

Purpose & Use
This project is intended solely as a personal and collaborative study tool to support preparation for the SC-200 Microsoft Security Operations Analyst certification. It is not for commercial distribution and is developed under the principles of fair dealing for educational purposes as outlined in the UK Copyright, Designs and Patents Act 1988.

Content Sourcing
Some test questions or data are derived from publicly available sources (e.g., YouTube), used solely for technical development, testing, and instructional design. Any content not original to the project will be subject to an internal audit to avoid infringement.

Your Role
As a contributor, you may provide code, content, feedback, or audit support. You retain rights to your original contributions, but by contributing, you grant permission for them to be used within the scope of this project.

Confidentiality
Until the project is reviewed and cleared for broader use or publication, all materials should be treated as internal and not shared externally.

No Warranties / Liability
This project is provided "as is" for educational use. The project lead and contributors accept no liability for how the tool is used beyond its intended scope.

Withdrawal
You are free to withdraw from the project at any time. If you wish to have your contributions removed, please notify the project lead.

```

