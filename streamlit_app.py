import importlib.util
from pathlib import Path
import traceback
import streamlit as st

st.set_page_config(page_title="制作室便利ツール", page_icon="🧪")

st.title("制作室便利ツール")

st.write("""
    左側のメニューから選択してください。
    """)


page = Path("pages/wavefunction.py")
spec = importlib.util.spec_from_file_location("wavefunction", page)
module = importlib.util.module_from_spec(spec)

try:
    spec.loader.exec_module(module)
    st.success("wavefunction.py imported successfully")
except Exception:
    st.code(traceback.format_exc())

st.page_link("pages/wavefunction.py", label="wavefunction plotter")
st.page_link("pages/smiles2svg.py", label="SMILES -> SVG")
