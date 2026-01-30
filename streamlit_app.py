import streamlit as st
import json
import subprocess

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
    with open("samples/deck.txt", "w", encoding="utf-8") as f:
        f.write(deck_file.getvalue().decode("utf-8"))
    with open("samples/ir.txt", "w", encoding="utf-8") as f:
        f.write(ir_file.getvalue().decode("utf-8"))

    if st.button("🔍 Run Consistency Check"):
        result = subprocess.run(
            ["python", "engine/main.py", "--deck", "samples/deck.txt", "--ir", "samples/ir.txt"],
            capture_output=True, text=True
        )

        try:
            output = json.loads(result.stdout.strip())
            st.subheader("✅ Findings")
            st.json(output)

            report_json = json.dumps(output, indent=2)
            st.download_button(
                label="📄 Download JSON Report",
                data=report_json,
                file_name="disclosure_consistency_report.json",
                mime="application/json"
            )
        except Exception as e:
            st.error("❌ Failed to parse output")
            st.code(result.stdout)
else:
    st.info("Please upload both files to begin.")
