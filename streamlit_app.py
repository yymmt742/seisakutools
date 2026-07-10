from pathlib import Path
import streamlit as st

st.set_page_config(page_title="制作室便利ツール", page_icon="🧪")

st.title("制作室便利ツール")

st.write("""
    左側のメニューから選択してください。
    """)

st.write("__file__=", __file__)
st.write("__cwd__=", (Path("pages")).exists())
st.write("pages exists =", (Path("pages")).exists())
st.write("pages =", list(Path("pages").glob("*")))
# st.page_link("pages/wavefunction.py", label="wavefunction plotter")
# st.page_link("pages/smiles2svg.py", label="SMILES -> SVG")
