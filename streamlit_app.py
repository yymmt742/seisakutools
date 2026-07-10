import streamlit as st

st.set_page_config(page_title="制作室便利ツール", page_icon="🧪")

st.title("制作室便利ツール")

st.write("""
    左側のメニューから選択してください。
    """)

pg = st.navigation(
    [
        st.Page("streamlit_app.py", title="トップページ", icon="🧪"),
        st.Page("pages/wavefunction.py", title="波動関数プロット"),
        st.Page("pages/smiles2svg.py", title="化学構造式描画"),
    ]
)

pg.run()
