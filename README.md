# Automatic Question Paper Generator (Bloom's Taxonomy)

> Introduction to Large Language Models: Course Project

A web app that builds exam question papers from a question bank. Each question is classified into a level of **Bloom's Taxonomy** (Remember, Understand, Apply, Analyze, Evaluate, Create) by an **LLM (Groq)**, with a rule-based classifier as a fallback. The bank supports several **question types** and is saved in **SQLite**. Papers are generated to match your chosen number of questions, total marks, difficulty and question types, and exported as **PDF, Word or text**.

## Overview

Setting a balanced question paper by hand is slow. The setter has to cover several topics, mix easy and hard questions, make the marks add up exactly, and ideally follow Bloom's Taxonomy so the paper tests more than recall. This project automates that process: build a question bank, let the LLM label each question, set your constraints, and get a ready-to-export paper in seconds.

## Features

- **LLM Bloom's classification** with confidence scores, cached in the database, and a **rule-based fallback** that reads the leading action verb.
- **Question types:** MCQ, fill in the blanks, true/false, assertion-reason, short, long and image-based. The type is read from the file or detected from the text.
- **Several ways to build a bank:** sample bank, CSV upload, manual entry (including a full-details form with options, answer and image), or generation from topics (offline templates or Groq AI).
- **Constraint-based paper generation:** hits your total marks, difficulty mix, Bloom's levels, question types and topic spread. Pick questions automatically or by hand, and swap any question.
- **Flexible sections:** group by marks, by question type, or automatically.
- **Question bank manager:** add, edit, delete, filter, change types, label with AI, download as CSV.
- **Classifier analytics:** accuracy, precision/recall/F1, confusion matrix and a TF-IDF + Logistic Regression baseline.
- **Export:** PDF, Word, text or print, including MCQ options and images.
- **Modern UI:** indigo/violet theme with dark mode and print-friendly styling.

## Bloom's Levels Used

| Level | Example verbs | Difficulty |
|---|---|---|
| Remember | Define, List, State | Easy |
| Understand | Explain, Describe | Easy |
| Apply | Implement, Solve | Medium |
| Analyze | Compare, Examine | Medium |
| Evaluate | Justify, Assess | Hard |
| Create | Design, Develop | Hard |

## Tech Stack

Python · Flask · SQLite · pandas · scikit-learn · ReportLab · python-docx · HTML/CSS/JavaScript · Groq API

## Project Structure

```
-Automatic-Question-Paper-Generator/
├── server.py              # Flask backend + REST API (main entry point)
├── db.py                  # SQLite storage (qpg.db)
├── llm_classifier.py      # LLM Bloom's classifier (Groq) with rule-based fallback
├── qtypes.py              # Question type detection, MCQ option parsing, filters
├── qpg.py                 # Rule-based classifier + paper generation (also a CLI)
├── export.py              # PDF and Word export
├── label_bank.py          # Label the sample bank with the LLM
├── compare_classifiers.py # Rule-based vs LLM on the sample bank
├── compare_hard.py        # Rule-based vs LLM on hard_test.csv
├── hard_test.csv          # Harder test set
├── test_llm.py            # Check the Groq key and model
├── list_models.py         # List models available to your key
├── app.py                 # Older Streamlit UI (optional)
├── questions.csv          # Sample bank (52 questions), seeds the DB on first run
├── qpg.db                 # SQLite database (auto-created, not committed)
├── uploads/images/        # Question images (auto-created, not committed)
└── static/index.html      # Frontend (single page)
```

## Setup and Run

**Requirements:** Python 3.9+, Git, and a free [Groq API key](https://console.groq.com) (optional; without it the app uses the rule-based classifier).

```bash
git clone https://github.com/Mahitha1229/-Automatic-Question-Paper-Generator.git
cd -Automatic-Question-Paper-Generator

python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate

pip install flask pandas reportlab python-docx requests scikit-learn

set GROQ_API_KEY=your_key_here   # PowerShell: $env:GROQ_API_KEY="..."  | macOS/Linux: export GROQ_API_KEY="..."

python server.py
```

Open **http://127.0.0.1:5000**. On the first run, `qpg.db` is created from `questions.csv`. Never commit your API key.

## How to Use

1. **Question Bank:** use the sample bank, upload a CSV, add questions, or generate them from topics. Click **AI label (Groq)** to classify unlabelled questions.
2. **Generate Paper:** choose Bloom's levels, question types, number of questions, total marks, difficulty and layout, then click **Generate paper**. Use **Swap** to replace a question or **Pick manually** to choose your own.
3. **Export:** download as PDF, Word or text, or print.

## How It Works

1. **Load a bank:** the questions are stored in SQLite and loaded into a pandas DataFrame.
2. **Classify:** each question uses its cached LLM label, or the rule-based label if it has none. Difficulty comes from the level: Remember/Understand = Easy, Apply/Analyze = Medium, Evaluate/Create = Hard.
3. **Generate:** the app samples up to 5000 candidate papers and scores each on how close it is to the target marks, the difficulty mix and the topic coverage. The best one is returned.
4. **Refine and export:** group the sections by marks or type, swap questions, then export as PDF, Word or text.

## Question Types

| Type | Stored as | Recognised by |
|---|---|---|
| Multiple choice | `mcq` | `type` column, option columns, or `(A) ... (B) ...` in the text |
| Fill in the blanks | `fib` | `____` or "fill in the blank" |
| True / False | `true_false` | "true or false" |
| Assertion and Reason | `assertion_reason` | Contains "Assertion" and "Reason" |
| Short answer | `short` | Default for up to 5 marks |
| Long answer | `long` | Default above 5 marks |
| Image-based | `image` | Has an image attached |

## CSV Format

```csv
question,topic,marks,type,option_a,option_b,option_c,option_d,answer
Define a stack.,Stack,2,short,,,,,
Which structure is LIFO?,Stack,1,mcq,Queue,Stack,Array,Heap,B
```

Only `question` is required. `topic` defaults to `General`, `marks` to `5`, and `type` is detected when empty. Optional `true_bloom_level` is used for analytics. Alternative headers such as `unit`, `chapter` and `correct answer` are recognised.

## Comparing the Classifiers

```bash
python label_bank.py            # label the sample bank with the LLM
python compare_classifiers.py   # rule-based vs LLM on the sample bank
python compare_hard.py          # rule-based vs LLM on hard_test.csv
```

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError` | Re-run the `pip install` command with the virtual environment active. |
| Port 5000 in use | Use `app.run(debug=True, port=5001)` in `server.py`. |
| Page looks old after an update | Hard-refresh with `Ctrl+F5`. |
| Groq `401` | API key missing or wrong. Check `GROQ_API_KEY`. |
| Groq `404` / model not found | Run `python list_models.py` and update `DEFAULT_MODEL` in `llm_classifier.py`. |
| Errors after updating the code | Stop the server, delete `qpg.db`, and restart. |
| "Total marks not exact" | The bank can't reach that total with the chosen questions. Use a different total or add questions with varied marks. |

## Notes

- Single-user demo: the active bank and paper are held in server memory; the bank itself is saved in SQLite.
- `qpg.db` and `uploads/` are in `.gitignore`. Download your bank as CSV to share it.
- Uploads accept CSV only. Review AI-generated questions and labels before real exam use.
- `debug=True` is for development only.

## Planned Work

- Upload banks from Excel, Word, PDF and images with automatic question extraction
- Suggest related questions for an uploaded question
- A marking scheme per question and a marks blueprint based on Bloom's levels

## Team

| Name | Roll No. |
|---|---|
| Mahitha Upadrasta | U23AI004 |
| Kavisha Vaja | U23AI016 |
| Budda Pallavi | U23AI061 |
| Jaimini Vasava | U23AI066 |
