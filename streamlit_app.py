import streamlit as st

st.set_page_config(page_title="制作室便利ツール", page_icon="🧪")

st.title("制作室便利ツール")

st.write("""
    左側のメニューから選択してください。
    """)

st.page_link("pages/wavefunction.py", label="波動関数プロット")
st.page_link("pages/smiles2svg.py", label="科学構造式描画")
