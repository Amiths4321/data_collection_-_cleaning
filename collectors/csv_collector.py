# collectors/csv_collector.py
import pandas as pd
from pathlib import Path

def extract_csv(filepath: str, text_columns: list[str] = None) -> dict:
    """
    Read CSV and convert text columns into readable prose for RAG.
    text_columns: which columns contain text to index.
                  If None, auto-detects string columns.
    """
    df     = pd.read_csv(filepath)
    issues = []

    # Check for issues
    null_counts = df.isnull().sum()
    for col, count in null_counts.items():
        if count > 0:
            issues.append(f"Column '{col}' has {count} missing values")

    duplicates = df.duplicated().sum()
    if duplicates:
        issues.append(f"{duplicates} duplicate rows found")
        df = df.drop_duplicates()

    # Auto-detect text columns if not specified
    if not text_columns:
        text_columns = [c for c in df.columns if df[c].dtype == object]

    # Convert rows to text blocks
    text_blocks = []
    for _, row in df.iterrows():
        parts = []
        for col in text_columns:
            if pd.notna(row.get(col)):
                parts.append(f"{col}: {row[col]}")
        if parts:
            text_blocks.append(" | ".join(parts))

    return {
        "source":   Path(filepath).name,
        "type":     "csv",
        "rows":     len(df),
        "columns":  list(df.columns),
        "issues":   issues,
        "raw_text": "\n\n".join(text_blocks)
    }