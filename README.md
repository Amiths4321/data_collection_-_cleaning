# Data Collection & Cleaning Pipeline

A production-ready data ingestion and cleaning pipeline built as **Step 2 & 3** of an end-to-end AI/LLM development workflow. Collects data from multiple sources, cleans it, masks PII, and outputs files ready for chunking and embedding into a RAG system.

---

## Where this fits in the AI development lifecycle

```
1. Problem Definition
2. Data Collection     ← this project (collect from PDF, CSV, Web)
3. Data Cleaning       ← this project (clean, normalise, mask PII)
4. Chunking
5. Embedding
6. Vector DB (RAG)
7. LLM + Agent
8. Evaluation
9. Deployment
10. Monitoring
```

---

## Features

- **Multi-source ingestion** — PDF, CSV, plain text, and live web URLs
- **Automatic cleaning** — fixes encoding errors, removes page numbers, collapses whitespace, strips non-printable characters
- **PII masking** — detects and masks emails, phone numbers, Aadhaar, PAN, and salary figures
- **Quality report** — JSON report with stats on every file processed
- **Streamlit UI** — drag-and-drop interface with live preview of cleaned output
- **RAG-ready output** — cleaned `.txt` files drop straight into `ingest.py`

---

## Project Structure

```
data_collection_&_cleaning/
│
├── pipeline.py              # end-to-end pipeline orchestrator
├── pipeline_app.py          # Streamlit web UI
├── quality_report.py        # standalone quality reporting
│
├── collectors/
│   ├── __init__.py
│   ├── pdf_collector.py     # extract text from PDF files (PyMuPDF)
│   ├── csv_collector.py     # read and validate CSV files (pandas)
│   └── web_collector.py     # scrape text from URLs (BeautifulSoup)
│
├── cleaners/
│   ├── __init__.py
│   ├── text_cleaner.py      # encoding fix, whitespace, noise removal
│   └── pii_masker.py        # mask emails, phones, Aadhaar, PAN, salary
│
├── raw_data/                # put your input files here
├── clean_data/              # cleaned output files saved here
│   └── quality_report.json  # auto-generated after each run
│
└── requirements.txt
```

---

## Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- Ollama running on remote GPU at `http://10.22.39.192:11434`

---

## Installation

```bash
# Clone or navigate to the project folder
cd data_collection_&_cleaning

# Activate your virtual environment
# Windows:
C:\Dev\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### `requirements.txt`

```
pymupdf
pandas
requests
beautifulsoup4
streamlit
```

---

## Running the App

```powershell
# Always run from the project root
cd "C:\Users\amith\Desktop\Confidential\Misc Projects\P2\data_collection_&_cleaning"

# Activate venv
C:\Dev\venv\Scripts\Activate.ps1

# Launch Streamlit UI
streamlit run pipeline_app.py
```

Open `http://localhost:8501` in your browser.

---

## Usage

### Via Streamlit UI

1. Select source type — **PDF**, **CSV**, **Text file**, or **Web URL**
2. Upload a file or paste a URL
3. Click **Run Pipeline**
4. View cleaning stats, PII masked, and a preview of the clean output
5. Find the cleaned file in `clean_data/`

### Via Python script

```python
from pipeline import process_file, run_pipeline

# Single file
result = process_file("hr_policy.pdf")

# Multiple sources at once
results = run_pipeline([
    "hr_policy.pdf",
    "employees.csv",
    "https://example.com/policy"
])
```

### Via command line

```powershell
python pipeline.py
```

---

## Pipeline Steps

Every source goes through 4 steps automatically:

```
[1] Collect   →  extract raw text from PDF / CSV / URL / TXT
[2] Clean     →  fix encoding, remove noise, collapse whitespace
[3] Mask PII  →  replace sensitive data with [EMAIL], [PHONE], etc.
[4] Save      →  write clean .txt to clean_data/ folder
```

---

## What Gets Cleaned

| Issue | Example (before) | After |
|---|---|---|
| Encoding artifact | `Employeesâ€™ leave` | `Employees' leave` |
| Page numbers | `\n14\n` | removed |
| Excessive whitespace | `leave   policy` | `leave policy` |
| Non-printable chars | `policy\x00doc` | `policydoc` |
| Empty lines | 5 blank lines | max 2 |

## What Gets Masked

| PII Type | Example (before) | After |
|---|---|---|
| Email | `hr@techcorp.com` | `[EMAIL]` |
| Phone | `9876543210` | `[PHONE]` |
| Aadhaar | `1234 5678 9012` | `[AADHAAR]` |
| PAN | `ABCDE1234F` | `[PAN]` |
| Salary | `Rs. 85,000` | `[SALARY]` |

---

## Output

Each processed file produces:

```
clean_data/
├── hr_policy_pdf_clean.txt       ← ready for chunking
├── employees_csv_clean.txt       ← ready for chunking
└── quality_report.json           ← stats for all files
```

### Sample `quality_report.json`

```json
[
  {
    "source": "hr_policy.pdf",
    "raw_chars": 12400,
    "cleaned_chars": 11100,
    "reduction_pct": 10.5,
    "cleaning_fixes": ["Removed standalone page numbers", "Collapsed excessive whitespace"],
    "pii_found": ["Emails: 2 found", "Phone numbers: 1 found"],
    "output_file": "clean_data/hr_policy_pdf_clean.txt"
  }
]
```

---

## Connecting to the RAG System

After cleaning, feed the output files directly into your RAG pipeline:

```powershell
# Copy clean files to rag_system documents folder
Copy-Item "clean_data\*_clean.txt" "..\rag_system\documents\"

# Re-index
cd ..\rag_system
python ingest.py
```

---

## Common Errors

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: collectors` | Missing `__init__.py` | Run `New-Item collectors\__init__.py -Force` |
| `ValueError: document closed` | PyMuPDF read after close | Use updated `pdf_collector.py` |
| `raw_data is a file not folder` | Created as file | Delete and `mkdir raw_data` |
| `csv_collectors not found` | Wrong filename (extra s) | Rename to `csv_collector.py` |

---

## Part of a Larger Project

This pipeline is **Step 2 & 3** of a full end-to-end AI system built across multiple projects:

| Step | Project |
|---|---|
| 1. Problem definition | `problem_definition/` — AI Project Validator |
| 2–3. Data collection & cleaning | `data_collection_&_cleaning/` — **this project** |
| 4–6. Chunking, embedding, vector DB | `rag_system/` — RAG pipeline |
| 7. Agent | `rag_system/rag_agent.py` |
| 8. Evaluation | `rag_system/eval/` — Ragas + LangSmith |
| 9. Web app | `rag_system/app.py` — Streamlit + FastAPI |
| 10. Support agent | `customer_support_agent/` |

---

## Author

Built as part of an AI Solution Architecture learning project.  
Model: `qwen2.5vl:latest` via Ollama on remote GPU `10.22.39.192:11434`

