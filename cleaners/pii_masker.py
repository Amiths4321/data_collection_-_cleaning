# cleaners/pii_masker.py
import re

def mask_pii(text: str) -> dict:
    """
    Detect and mask personally identifiable information.
    Returns masked text + list of what was found.
    """
    found = []

    # Email addresses
    emails = re.findall(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", text, re.IGNORECASE)
    if emails:
        found.append(f"Emails: {len(emails)} found")
        text = re.sub(r"\b[\w.+-]+@[\w-]+\.[a-z]{2,}\b", "[EMAIL]", text, flags=re.IGNORECASE)

    # Phone numbers (Indian + international)
    phones = re.findall(r"(\+91[\s-]?)?[6-9]\d{9}|\+\d{1,3}[\s-]\d{4,}", text)
    if phones:
        found.append(f"Phone numbers: {len(phones)} found")
        text = re.sub(r"(\+91[\s-]?)?[6-9]\d{9}", "[PHONE]", text)

    # Aadhaar numbers (12 digits)
    aadhaars = re.findall(r"\b\d{4}\s\d{4}\s\d{4}\b", text)
    if aadhaars:
        found.append(f"Aadhaar numbers: {len(aadhaars)} found")
        text = re.sub(r"\b\d{4}\s\d{4}\s\d{4}\b", "[AADHAAR]", text)

    # Salary figures (Rs. followed by numbers)
    salaries = re.findall(r"Rs\.?\s*[\d,]+", text, re.IGNORECASE)
    if salaries:
        found.append(f"Salary figures: {len(salaries)} found")
        text = re.sub(r"Rs\.?\s*[\d,]+", "[SALARY]", text, flags=re.IGNORECASE)

    # PAN numbers
    pans = re.findall(r"\b[A-Z]{5}\d{4}[A-Z]\b", text)
    if pans:
        found.append(f"PAN numbers: {len(pans)} found")
        text = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]\b", "[PAN]", text)

    return {
        "masked_text": text,
        "pii_found":   found,
        "pii_count":   len(found)
    }