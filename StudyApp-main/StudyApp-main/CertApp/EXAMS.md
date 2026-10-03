# Exam selection

Launch the desktop application from this folder:

```powershell
python main.py
python main.py --dark
```

Choose SC-200 (375 questions), SC-300 (408 questions), or SC-500 (120 questions), enter a question count, and select **Start Quiz**. **Choose another exam** on the results screen returns to the picker.

Progress, missed questions and score history are stored separately in `data/sc-200`, `data/sc-300`, and `data/sc-500`. Existing SC-200 progress is copied on first use; the original files are retained. Custom banks supplied with `--file` receive their own storage directory.

Image questions use numbered menus matching the order of the source boxes or statements. Choices can be reused, including repeated Yes/No answers. All boxes must match to score the question. Click an image to open it at full resolution. Source solution images and clickable references appear after submission.

## SC-300 source and import notes

- Source: user-supplied `SC-300_en.pdf`, 380 pages.
- 408 questions, retaining the PDF question numbers and page references.
- 143 image-based or simulation questions have explicit answer mappings; three image-selection questions use checkboxes and the others use ordered menus.
- 472 question and solution images are included. The PDF itself is not included.
- 19 simulations are adapted into ordered solution steps. These exercise recall of the supplied solution rather than operating a live Azure environment.
- Existing explanations and references are retained. Where no explanation is provided, the app displays a labelled answer-key summary and available source solution images.
- Answers follow this PDF, including potentially outdated or inconsistent answers. They have not been independently certified against current Microsoft product behaviour.
- Shared Contoso and ADatum case-study text is restored where the corresponding scenario appears elsewhere in the PDF. Question 400 uses the scenario and server table from its explanation.
- Questions 390, 391, 392, 393, 395, 398, 399, 407 and 408 refer to requirements missing from the supplied PDF. Each displays a source-context notice. Their supplied answers remain available.

## Validation

```powershell
python main.py --validate --file questions/sc-200.json
python main.py --validate --file questions/sc-300.json
python -m pytest tests -q
```

Tests cover both bank counts, image decoding, every answer key, exam selection, progress isolation, legacy migration, checkbox mouse release in light/dark modes, interactive answer submission and duplicate-submit prevention.

This change is for the desktop application. The separate Android project has its own question data and UI.

## SC-500

SC-500 includes 120 questions across four topics, including 36 image-based questions with ordered menus. Shared case-study text and tables are included with 17 questions. See [SC-500 source notes](SC500.md), including the printed answer/explanation conflict in question 96.

Validate with `python main.py --validate --file questions/sc-500.json`.
