import numpy as np
from PIL import Image, ImageDraw
import streamlit as st
import io

st.set_page_config(page_title="Gravity lens raytracer", page_icon="🕳️")

st.title("gravity lens raytracer (小角近似)")

uploaded_file = st.file_uploader(
    "画像をアップロード",
    type=["png", "jpg", "jpeg", "bmp", "tif", "tiff"],
)


def sample_image(
    N: int = 256,
    offset: tuple[int] = (0, 15),
    radius: int = 10,
) -> Image.Image:

    c = N // 2
    img = Image.new("RGB", (N, N), "black")
    draw = ImageDraw.Draw(img)
    draw.ellipse(
        (
            c - radius + offset[0],
            c - radius + offset[1],
            c + radius + offset[0],
            c + radius + offset[1],
        ),
        fill="white",
    )
    return img


# ==========================================================
# Ray tracing
# ==========================================================


def ray_tracer(
    img: Image.Image,
    thetaE: float = 0.18,  # Einstein radius (image coordinate)
    FOV: float = 2.0,  # coordinate = [-FOV, FOV]
) -> Image.Image:

    _img = np.asarray(img).astype(np.float32) / 255.0
    H, W = _img.shape[:2]

    out = np.zeros_like(_img)

    for iy in range(H):
        for ix in range(W):
            theta_x, theta_y = pixel_to_coord(ix, iy, W, H, FOV)
            beta_x, beta_y = lens(theta_x, theta_y, thetaE)
            sx, sy = coord_to_pixel(beta_x, beta_y, W, H, FOV)
            out[iy, ix] = bilinear(_img, sx, sy)

    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


# ==========================================================
# Bilinear interpolation
# ==========================================================


def bilinear(im, x, y):

    h, w = im.shape[:2]

    _x = w - 2 if x >= w - 1 else (0 if x < 0 else x)
    _y = h - 2 if y >= h - 1 else (0 if y < 0 else y)

    x0 = int(np.floor(_x))
    y0 = int(np.floor(_y))

    dx = _x - x0
    dy = _y - y0

    c00 = im[y0, x0]
    c10 = im[y0, x0 + 1]
    c01 = im[y0 + 1, x0]
    c11 = im[y0 + 1, x0 + 1]

    return (
        (1 - dx) * (1 - dy) * c00
        + dx * (1 - dy) * c10
        + (1 - dx) * dy * c01
        + dx * dy * c11
    )


# ==========================================================
# Lens equation
#
# theta -> beta
#
# ==========================================================


def lens(theta_x, theta_y, thetaE):

    r2 = theta_x**2 + theta_y**2 + 1e-12

    alpha_x = thetaE**2 * theta_x / r2
    alpha_y = thetaE**2 * theta_y / r2

    beta_x = theta_x - alpha_x
    beta_y = theta_y - alpha_y

    return beta_x, beta_y


# ==========================================================
# Coordinate conversion
# ==========================================================


def coord_to_pixel(x: int, y: int, W: int, H: int, FOV: float) -> tuple[float]:

    px = (x / (FOV * W / H) + 1) * 0.5 * (W - 1)
    py = (1 - (y / FOV + 1) * 0.5) * (H - 1)

    return px, py


def pixel_to_coord(ix: int, iy: int, W: int, H: int, FOV: float) -> tuple[float]:

    x = (ix / (W - 1) * 2 - 1) * FOV * W / H
    y = ((1 - iy / (H - 1)) * 2 - 1) * FOV

    return x, y


if uploaded_file is None:
    image = sample_image()
else:
    image = Image.open(uploaded_file)

preview = image.copy()
preview.thumbnail((256, 256))

thetaE = st.slider(r"$\theta_E$ (アインシュタイン半径)", 0.0, 0.5, 0.15)
FOV = st.slider("カメラの視野", 0.1, 5.0, 2.0)

result = ray_tracer(preview, thetaE, FOV)

col1, col2 = st.columns(2)
with col1:
    st.subheader("入力")
    st.image(preview)

with col2:
    st.subheader("出力（プレビュー）")
    st.image(result)

if st.button("画像処理を開始"):
    with st.spinner("画像処理中..."):
        result = ray_tracer(image, thetaE, FOV)
        buf = io.BytesIO()
        result.save(buf, "PNG")
        st.download_button(
            "ダウンロード",
            data=buf.getvalue(),
            file_name="result.png",
            mime="image/png",
        )
