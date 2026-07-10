Warning: Python 3.12 cannot parse code formatted for Python 3.15. To fix this: run Black with Python 3.15, set --target-version to py312, or use --fast to skip the safety check. Black's safety check verifies equivalence by parsing the AST, which fails when the running Python is older than the target version.
import streamlit as st

st.set_page_config(page_title="制作室便利ツール", page_icon="🧪")

st.title("制作室便利ツール")

st.write("""
    左側のメニューから選択してください。
    """)

st.page_link("pages/wavefunction.py", label="wavefunction plotter")
st.page_link("pages/smiles2svg.py", label="SMILES -> SVG")
