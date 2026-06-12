# cleaners/text_cleaner.py
import re
import unicodedata

def clean_text(text: str, source_name: str = "") -> dict:
    """
    Full cleaning pipeline for any text.
    Returns cleaned text + list of what was fixed.
    """
    original_len = len(text)
    fixes        = []

    # 1. Fix encoding issues
    text = fix_encoding(text)

    # 2. Remove page numbers (standalone numbers on their own line)
    before = len(text)
    text   = re.sub(r"^\s*\d{1,3}\s*$", "", text, flags=re.MULTILINE)
    if len(text) < before:
        fixes.append("Removed standalone page numbers")

    # 3. Remove headers/footers patterns
    before = len(text)
    text   = re.sub(r"(CONFIDENTIAL|DRAFT|Page \d+ of \d+|www\.\S+)", "", text, flags=re.IGNORECASE)
    if len(text) < before:
        fixes.append("Removed headers/footers/URLs")

    # 4. Collapse excessive whitespace
    before = len(text)
    text   = re.sub(r"\n{3,}", "\n\n", text)
    text   = re.sub(r"[ \t]{2,}", " ", text)
    if len(text) < before:
        fixes.append("Collapsed excessive whitespace")

    # 5. Remove non-printable characters
    before = len(text)
    text   = "".join(c for c in text if c.isprintable() or c in "\n\t")
    if len(text) < before:
        fixes.append("Removed non-printable characters")

    # 6. Normalise unicode
    text = unicodedata.normalize("NFKC", text)

    # 7. Strip leading/trailing whitespace
    text = text.strip()

    cleaned_len = len(text)
    reduction   = round((1 - cleaned_len / original_len) * 100, 1) if original_len else 0

    return {
        "cleaned_text":   text,
        "original_chars": original_len,
        "cleaned_chars":  cleaned_len,
        "reduction_pct":  reduction,
        "fixes_applied":  fixes
    }


def fix_encoding(text: str) -> str:
    """Fix common encoding artifacts from PDF extraction."""
    replacements = {
        "\u00e2\u0080\u0099": "'",
        "\u00e2\u0080\u009c": '"',
        "\u00e2\u0080\u009d": '"',
        "\u00e2\u0080\u0098": "'",
        "\u00e2\u0080\u00a6": "...",
        "\u00e2\u0080\u0094": "-",     # em dash
        "\u00e2\u0080\u0093": "-",     # en dash
        "\u00c2\u00a9":       "(c)",   # copyright
        "\u00c2\u00ae":       "(r)",   # registered
        "\u00c3\u00a9":       "e",
        "\u00c3\u00a8":       "e",
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)
    return text