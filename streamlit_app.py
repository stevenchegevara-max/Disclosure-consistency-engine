import streamlit as st
import json

st.set_page_config(page_title="Disclosure Consistency Engine", page_icon="📊", layout="centered")

st.markdown("""
    <style>
        .reportview-container {
            padding-top: 2rem;
        }
        .block-container {
            padding: 2rem 2rem;
            border-radius: 12px;
            background-color: #f9fafb;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
        }
    </style>
""", unsafe_allow_html=True)

st.image("https://img.icons8.com/color/96/combo-chart--v1.png", width=70)
st.title("Disclosure Consistency Engine")
st.caption("Detect inconsistencies across investor-facing documents.")

st.markdown("#### 📁 Upload Your Files")
deck_file = st.file_uploader("Upload Investor Deck (.txt)", type="txt")
ir_file = st.file_uploader("Upload IR Site Content (.txt)", type="txt")

if deck_file and ir_file:
    deck_text = deck_file.read().decode("utf-8")
    ir_text = ir_file.read().decode("utf-8")

    # Simple numeric mismatch detection
    import re

    def extract_euro_numbers(text):
        return re.findall(r'€\s?\d+[.,]?\d*\s?[MB]?', text)

    deck_numbers = set(extract_euro_numbers(deck_text))
    ir_numbers = set(extract_euro_numbers(ir_text))

    mismatches = list(deck_numbers.symmetric_difference(ir_numbers))

    st.markdown("### 🔍 Detected Inconsistencies")
    if mismatches:
        issues = []
        for value in mismatches:
            issues.append({
                "issue_type": "numeric_mismatch",
                "metric": "REVENUE",  # Placeholder
                "deck_value": value if value in deck_numbers else "",
                "ir_value": value if value in ir_numbers else "",
                "recommended_action": "Align the metric value across documents."
            })
        st.json(issues)
        st.success(f"{len(issues)} issue(s) found.")
    else:
        st.success("No numeric mismatches found! 🎉")

    if st.button("📄 Download JSON Report"):
        report = json.dumps(issues, indent=2)
        st.download_button(
            label="Download JSON",
            data=report,
            file_name="disclosure_report.json",
            mime="application/json"
        )

else:
    st.info("Please upload both files to begin.")
