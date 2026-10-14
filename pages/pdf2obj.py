import pymupdf  # PyMuPDF
import sys
import math
import streamlit as st
import io
import zipfile
from pathlib import Path

st.set_page_config(page_title="pdf to obj", page_icon="📄")
st.title("pdf to obj")
uploaded_file = st.file_uploader(
    "pdfをアップロード",
    type=["pdf"],
)


# ============================================================
# Cubic Bezier
# P0 -> P3
# P1, P2 が制御点
# ============================================================


def cubic_bezier(p0, p1, p2, p3, t):
    u = 1.0 - t
    x = u**3 * p0[0] + 3 * u**2 * t * p1[0] + 3 * u * t**2 * p2[0] + t**3 * p3[0]
    y = u**3 * p0[1] + 3 * u**2 * t * p1[1] + 3 * u * t**2 * p2[1] + t**3 * p3[1]
    return (x, y)


# ============================================================
# PDF drawing -> polygon
# ============================================================


def drawing_to_polygon(drawing):
    """
    drawingから閉じたパスの頂点列を取得。
    """

    items = drawing["items"]

    points = []
    current = None
    start = None

    for item in items:

        command = item[0]

        # ----------------------------------------------------
        # line
        # ('l', p1, p2)
        # ----------------------------------------------------
        if command == "l":
            p1 = item[1]
            p2 = item[2]

            if current is None:
                points.append((p1.x, p1.y))
                start = (p1.x, p1.y)

            points.append((p2.x, p2.y))
            current = (p2.x, p2.y)

        # ----------------------------------------------------
        # cubic Bezier
        #
        # ('c', p1, p2, p3, p4)
        # ----------------------------------------------------
        elif command == "c":

            p0 = item[1]
            p1 = item[2]
            p2 = item[3]
            p3 = item[4]

            p0 = (p0.x, p0.y)
            p1 = (p1.x, p1.y)
            p2 = (p2.x, p2.y)
            p3 = (p3.x, p3.y)

            if current is None:
                points.append(p0)
                start = p0

            # p0 -> p3
            for i in range(1, BEZIER_STEPS + 1):
                t = i / BEZIER_STEPS
                points.append(cubic_bezier(p0, p1, p2, p3, t))

            current = p3

        # ----------------------------------------------------
        # rectangle
        #
        # ('re', rect, ...)
        # ----------------------------------------------------
        elif command == "re":

            rect = item[1]

            x0 = rect.x0
            y0 = rect.y0
            x1 = rect.x1
            y1 = rect.y1

            points = [
                (x0, y0),
                (x1, y0),
                (x1, y1),
                (x0, y1),
            ]

            start = points[0]
            current = points[-1]

    # --------------------------------------------------------
    # closePath
    # --------------------------------------------------------

    # if not drawing.get("closePath", False):
    #    return None

    if len(points) < 3:
        return None

    # 最後と最初が同じなら最後を削除
    if points[0] == points[-1]:
        points.pop()

    return points


# ============================================================
# OBJ出力
# ============================================================


def polygons2obj(polygons, FLIP_Y: bool):

    s = "# Generated from PDF using PyMuPDF\n"
    vertex_offset = 0

    for poly_index, polygon in enumerate(polygons):

        s += f"\ng polygon_{poly_index}\n"

        # vertices
        for x, y in polygon:

            if FLIP_Y:
                s += f"v {x:.6f} {-y:.6f} 0.000000\n"
            else:
                s += f"v {x:.6f} {y:.6f} 0.000000\n"

        n = len(polygon)
        indices = [str(vertex_offset + i + 1) for i in range(n)]
        s += "f " + " ".join(indices) + "\n"
        vertex_offset += n

    return s


def pdf2obj(pdf_data: bytes):

    doc = pymupdf.open(stream=pdf_data, filetype="pdf")

    objs = []

    for page in doc:
        polygons = []
        drawings = page.get_drawings()

        for i, drawing in enumerate(drawings):

            polygon = drawing_to_polygon(drawing)
            if polygon is None:
                continue
            polygons.append(polygon)

        objs.append(polygons2obj(polygons, FLIP_Y))

    return objs


def create_zip(objs: list[str], stem: str) -> bytes:

    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
    ) as zf:

        for i, obj in enumerate(objs):
            obj_text = process_page(page)
            filename = f"{stem}_{i + 1:04d}.obj"
            zf.writestr(filename, obj_text)

    return zip_buffer.getvalue()


# ============================================================
# 設定
# ============================================================

# Bezier曲線を何分割するか
BEZIER_STEPS = 20
# PDF座標系はYが下向きなのでYを反転
FLIP_Y = True


if uploaded_file is not None:
    st.write(f"入力ファイル: `{uploaded_file.name}`")

    # ファイル名からstemを取得
    pdf_file = Path(uploaded_file.name)
    pdf_data = uploaded_file.getvalue()
    objs = pdf2obj(pdf_data)

    if len(objs) > 1:
        st.download_button(
            label="ダウンロード",
            data=create_zip(objs, stem),
            file_name=pdf_file.with_suffix(".zip").name,
            mime="application/zip",
        )
    else:
        st.download_button(
            label="ダウンロード",
            data=objs[0],
            file_name=pdf_file.with_suffix(".obj").name,
            mime="text/plain",
        )
