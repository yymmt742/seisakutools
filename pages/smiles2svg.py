import streamlit as st

from rdkit import Chem
from rdkit.Chem import rdDepictor
from rdkit.Chem.Draw import rdMolDraw2D

st.set_page_config(page_title="Chemical fomula")

st.title("化学構造式描画")

smiles = st.text_input("SMILES", "CC(C)Oc1ccccc1C(=O)O")

width = st.slider("Width", 200, 1200, 500)
height = st.slider("Height", 200, 1200, 400)

if smiles:
    mol = Chem.MolFromSmiles(smiles)

    if mol is None:
        st.error("Invalid SMILES")
    else:
        # CoordGenを利用
        rdDepictor.SetPreferCoordGen(True)
        rdDepictor.Compute2DCoords(mol)

        drawer = rdMolDraw2D.MolDraw2DSVG(width, height)

        opts = drawer.drawOptions()
        opts.padding = 0.05
        opts.fixedBondLength = 35
        opts.clearBackground = True

        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()

        svg = drawer.GetDrawingText()

        if svg.startswith("<?xml"):
            svg = svg.split("?>", 1)[1]

        st.subheader("Preview")
        st.image(svg)

        st.download_button(
            "Download SVG",
            svg,
            file_name="molecule.svg",
            mime="image/svg+xml",
        )
