import streamlit as st

st.set_page_config(page_title="制作室便利ツール", page_icon="🧪")

st.title("制作室便利ツール")

st.write("""
    左側のメニューから選択してください。
    """)

try:
    spec.loader.exec_module(module)
    st.success("wavefunction.py imported successfully")
except Exception:
    st.code(traceback.format_exc())

st.page_link("pages/wavefunction.py", label="wavefunction plotter")
st.page_link("pages/smiles2svg.py", label="SMILES -> SVG")
