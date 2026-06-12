# pipeline.py
import os
import json
from pathlib import Path
from datetime import datetime

from collectors.pdf_collector import extract_pdf
from collectors.csv_collector import extract_csv
from collectors.web_collector import extract_url
from cleaners.text_cleaner    import clean_text
from cleaners.pii_masker      import mask_pii

RAW_DIR   = Path("raw_data")
CLEAN_DIR = Path("clean_data")

def process_file(source: str) -> dict:
    """
    Auto-detect source type and run full pipeline:
    collect → clean → mask PII → save
    """
    CLEAN_DIR.mkdir(exist_ok=True)
    result = {"source": source, "timestamp": datetime.now().isoformat()}

    # Step 1 — Collect
    print(f"\n  [1] Collecting: {source}")
    if source.endswith(".pdf"):
        collected = extract_pdf(str(RAW_DIR / source))
    elif source.endswith(".csv"):
        collected = extract_csv(str(RAW_DIR / source))
    elif source.startswith("http"):
        collected = extract_url(source)
    else:
        return {"source": source, "error": "Unsupported source type"}

    raw_text = collected.get("raw_text", "")
    result["collection_issues"] = collected.get("issues", [])
    result["raw_chars"]         = len(raw_text)
    print(f"     Extracted {len(raw_text)} characters")

    if not raw_text.strip():
        result["error"] = "No text extracted"
        return result

    # Step 2 — Clean
    print(f"  [2] Cleaning...")
    cleaned = clean_text(raw_text, source)
    result["cleaning_fixes"]  = cleaned["fixes_applied"]
    result["cleaned_chars"]   = cleaned["cleaned_chars"]
    result["reduction_pct"]   = cleaned["reduction_pct"]
    print(f"     Reduced by {cleaned['reduction_pct']}%")

    # Step 3 — Mask PII
    print(f"  [3] Masking PII...")
    masked = mask_pii(cleaned["cleaned_text"])
    result["pii_found"] = masked["pii_found"]
    final_text = masked["masked_text"]
    print(f"     PII items masked: {masked['pii_count']}")

    # Step 4 — Save clean output
    safe_name = source.replace("/", "_").replace(":", "").replace(".", "_")
    out_path  = CLEAN_DIR / f"{safe_name}_clean.txt"
    out_path.write_text(final_text, encoding="utf-8")
    result["output_file"] = str(out_path)
    print(f"  [4] Saved: {out_path}")

    return result


def run_pipeline(sources: list[str]) -> list[dict]:
    """Run pipeline on multiple sources."""
    print(f"Starting pipeline for {len(sources)} sources...")
    results = []
    for src in sources:
        try:
            res = process_file(src)
        except Exception as e:
            res = {"source": src, "error": str(e)}
        results.append(res)

    # Save quality report
    report_path = CLEAN_DIR / "quality_report.json"
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\nQuality report saved: {report_path}")
    return results


if __name__ == "__main__":
    # Example: process your existing TechCorp documents
    RAW_DIR.mkdir(exist_ok=True)

    # Copy your existing txt files as sources
    sources = [
        "hr_policy.txt",            # treat as text
        "https://en.wikipedia.org/wiki/Leave_of_absence",  # web
    ]

    # For txt files use pdf collector logic simply
    for src in sources:
        if src.endswith(".txt") and not src.startswith("http"):
            path = RAW_DIR / src
            if not path.exists():
                # Copy from rag_system documents
                import shutil
                shutil.copy(
                    f"../rag_system/documents/{src}",
                    str(path)
                )

    results = run_pipeline(sources)
    for r in results:
        print(f"\n{r['source']}: {r.get('cleaned_chars', 0)} chars clean, "
              f"{len(r.get('pii_found', []))} PII items")