import streamlit as st
import json
import subprocess

st.set_page_config(page_title="Disclosure Consistency Engine", layout="wide")
st.title("📊 Disclosure Consistency Engine")

st.markdown("Upload your investor-facing documents (as `.txt`) to detect inconsistencies.")

deck_file = st.file_uploader("Upload Deck (.txt)", type=["txt"])
ir_file = st.file_uploader("Upload IR Site (.txt)", type=["txt"])

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
            output = json.loads(result.stdout.split(">>")[-1].strip())
            st.subheader("✅ Findings")
            st.json(output)
        except Exception as e:
            st.error("❌ Failed to parse output")
            st.code(result.stdout)
else:
    st.info("Please upload both files to begin.")
