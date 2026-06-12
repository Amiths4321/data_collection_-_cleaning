# pipeline_app.py
# streamlit run pipeline_app.py

import streamlit as st
import json
from pathlib import Path
from pipeline import process_file, CLEAN_DIR

st.set_page_config(page_title="Data Pipeline", page_icon="🔧", layout="wide")
st.title("🔧 Data Collection & Cleaning Pipeline")
st.caption("Step 2 & 3 of AI development — before chunking and embedding")

tab1, tab2 = st.tabs(["Process Data", "Quality Report"])

with tab1:
    st.subheader("Add a data source")
    source_type = st.radio(
        "Source type", ["PDF file", "CSV file", "Web URL"], horizontal=True
    )

    if source_type in ["PDF file", "CSV file"]:
        uploaded = st.file_uploader(
            "Upload file",
            type=["pdf", "csv"]
        )
        if uploaded:
            # Save to raw_data/
            Path("raw_data").mkdir(exist_ok=True)
            save_path = Path("raw_data") / uploaded.name
            save_path.write_bytes(uploaded.read())
            source = uploaded.name
            st.success(f"Uploaded: {uploaded.name}")
        else:
            source = None
    else:
        source = st.text_input(
            "Enter URL",
            placeholder="https://example.com/policy"
        )

    if st.button("Run Pipeline", type="primary") and source:
        with st.spinner("Collecting → Cleaning → Masking PII..."):
            result = process_file(source)

        if "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            # Metrics
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Raw chars",     result.get("raw_chars", 0))
            c2.metric("Clean chars",   result.get("cleaned_chars", 0))
            c3.metric("Reduced by",    f"{result.get('reduction_pct', 0)}%")
            c4.metric("PII masked",    len(result.get("pii_found", [])))

            # Issues
            issues = result.get("collection_issues", [])
            if issues:
                st.warning("Collection issues:\n" + "\n".join(f"- {i}" for i in issues))

            # Fixes
            fixes = result.get("cleaning_fixes", [])
            if fixes:
                st.info("Cleaning applied:\n" + "\n".join(f"- {f}" for f in fixes))

            # PII
            pii = result.get("pii_found", [])
            if pii:
                st.warning("PII masked:\n" + "\n".join(f"- {p}" for p in pii))

            # Preview clean output
            out = Path(result["output_file"])
            if out.exists():
                st.subheader("Clean output preview")
                st.text_area(
                    "First 1000 chars",
                    out.read_text(encoding="utf-8")[:1000],
                    height=200
                )
                st.success(f"✅ Ready for chunking → {result['output_file']}")

with tab2:
    st.subheader("Quality Report")
    report_path = CLEAN_DIR / "quality_report.json"

    if report_path.exists():
        report = json.loads(report_path.read_text())
        for r in report:
            status = "✅" if "error" not in r else "❌"
            with st.expander(f"{status} {r['source']}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Raw chars",   r.get("raw_chars", 0))
                c2.metric("Clean chars", r.get("cleaned_chars", 0))
                c3.metric("Reduction",   f"{r.get('reduction_pct', 0)}%")

                if r.get("pii_found"):
                    st.warning("PII found: " + ", ".join(r["pii_found"]))
                if r.get("collection_issues"):
                    st.error("Issues: " + ", ".join(r["collection_issues"]))
    else:
        st.info("No report yet. Process some files first.")