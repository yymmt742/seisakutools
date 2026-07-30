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
    offX: float = 0.0,
    offY: float = 0.0,
) -> Image.Image:

    _img = np.asarray(img).astype(np.float32)
    if _img.max() > 1:
        img /= 255.0
    out = np.zeros_like(_img)

    # ==========================================================
    # Image coordinate -> Coordinate
    # ==========================================================

    H, W = _img.shape[:2]
    aspect = W / H
    x = np.linspace(-FOV * aspect, FOV * aspect, W) + offX
    y = np.linspace(-FOV, FOV, H) + offY
    theta_x, theta_y = np.meshgrid(x, y)

    # ==========================================================
    # Lens equation
    #
    # theta -> beta
    #
    # ==========================================================

    r2 = theta_x**2 + theta_y**2 + 1e-12
    alpha_x = thetaE**2 * theta_x / r2
    alpha_y = thetaE**2 * theta_y / r2
    beta_x = theta_x - alpha_x - offX
    beta_y = theta_y - alpha_y - offY

    # ==========================================================
    # Coordinate -> Image coordinate
    # ==========================================================

    sx = (beta_x / (FOV * aspect) + 1) * 0.5 * (W - 1)
    sy = (1 - (beta_y / FOV + 1) * 0.5) * (H - 1)

    # ==========================================================
    # Bilinear interpolation
    # ==========================================================

    x0 = np.floor(sx).astype(np.int32)
    y0 = np.floor(sy).astype(np.int32)
    dx = sx - x0
    dy = sy - y0
    x0 = np.clip(x0, 0, W - 2)
    y0 = np.clip(y0, 0, H - 2)

    c00 = _img[y0, x0]
    c10 = _img[y0, x0 + 1]
    c01 = _img[y0 + 1, x0]
    c11 = _img[y0 + 1, x0 + 1]

    dx = dx[..., None]
    dy = dy[..., None]
    out = (
        (1 - dx) * (1 - dy) * c00
        + dx * (1 - dy) * c10
        + (1 - dx) * dy * c01
        + dx * dy * c11
    )

    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


if uploaded_file is None:
    image = sample_image()
else:
    image = Image.open(uploaded_file)

preview = image.copy()
preview.thumbnail((256, 256))

thetaE = st.slider(r"$\theta_E$ (アインシュタイン半径)", 0.0, 0.5, 0.15)
FOV = st.slider("カメラの視野", 0.1, 5.0, 2.0)
offX = st.slider("オフセットX", -1.0, 1.0, 0.0)
offY = st.slider("オフセットY", -1.0, 1.0, 0.0)

result = ray_tracer(preview, thetaE, FOV, offX, offY)

col1, col2 = st.columns(2)
with col1:
    st.subheader("入力")
    st.image(preview)

with col2:
    st.subheader("出力（プレビュー）")
    st.image(result)

if st.button("画像処理を開始"):
    with st.spinner("画像処理中..."):
        result = ray_tracer(image, thetaE, FOV, offX, offY)
        buf = io.BytesIO()
        result.save(buf, "PNG")
        st.download_button(
            "ダウンロード",
            data=buf.getvalue(),
            file_name="result.png",
            mime="image/png",
        )
