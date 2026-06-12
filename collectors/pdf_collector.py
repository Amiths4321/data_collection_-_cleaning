# collectors/pdf_collector.py
import fitz
from pathlib import Path

def extract_pdf(filepath):
    doc        = fitz.open(filepath)
    pages      = []
    issues     = []
    total_pages = doc.page_count   # read BEFORE closing

    for i in range(total_pages):
        page = doc[i]
        text = page.get_text().strip()

        if not text:
            issues.append(f"Page {i+1} is empty or image-only")
            continue

        if len(text) < 50:
            issues.append(f"Page {i+1} has very little text ({len(text)} chars)")

        pages.append({
            "page":  i + 1,
            "text":  text,
            "chars": len(text)
        })

    raw_text = "\n\n".join(p["text"] for p in pages)
    doc.close()   # close AFTER reading everything

    return {
        "source":       Path(filepath).name,
        "type":         "pdf",
        "total_pages":  total_pages,
        "pages":        pages,
        "issues":       issues,
        "raw_text":     raw_text
    }