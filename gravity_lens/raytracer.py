import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

N = 800

img = Image.new("RGB", (N, N), "black")
draw = ImageDraw.Draw(img)
draw.ellipse((400, 400, 420, 420), fill="white")

# img.save("background.png")

# ==========================================================
# Parameters
# ==========================================================

# IMAGE = "background.png"

thetaE = 0.18  # Einstein radius (image coordinate)
FOV = 2.0  # coordinate = [-FOV, FOV]

# ==========================================================
# Read image
# ==========================================================

# img = Image.open(IMAGE).convert("RGB")
img = np.asarray(img).astype(np.float32) / 255.0

H, W = img.shape[:2]


# ==========================================================
# Bilinear interpolation
# ==========================================================


def bilinear(im, x, y):

    h, w = im.shape[:2]

    if x < 0 or x >= w - 1 or y < 0 or y >= h - 1:
        return np.zeros(3)

    x0 = int(np.floor(x))
    y0 = int(np.floor(y))

    dx = x - x0
    dy = y - y0

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


def lens(theta_x, theta_y):

    r2 = theta_x**2 + theta_y**2 + 1e-12

    alpha_x = thetaE**2 * theta_x / r2
    alpha_y = thetaE**2 * theta_y / r2

    beta_x = theta_x - alpha_x
    beta_y = theta_y - alpha_y

    return beta_x, beta_y


# ==========================================================
# Coordinate conversion
# ==========================================================


def coord_to_pixel(x, y):

    px = (x / FOV + 1) / 2 * (W - 1)
    py = (1 - (y / FOV + 1) / 2) * (H - 1)

    return px, py


def pixel_to_coord(ix, iy):

    x = (ix / (W - 1) * 2 - 1) * FOV
    y = ((1 - iy / (H - 1)) * 2 - 1) * FOV

    return x, y


# ==========================================================
# Ray tracing
# ==========================================================

out = np.zeros_like(img)

for iy in range(H):

    for ix in range(W):

        theta_x, theta_y = pixel_to_coord(ix, iy)

        beta_x, beta_y = lens(theta_x, theta_y)

        sx, sy = coord_to_pixel(beta_x, beta_y)

        out[iy, ix] = bilinear(img, sx, sy)


# ==========================================================
# Plot
# ==========================================================

fig, ax = plt.subplots(1, 2, figsize=(12, 6))

ax[0].imshow(img)
ax[0].set_title("Background")

ax[1].imshow(out)
ax[1].set_title("Lensed image")

plt.tight_layout()
plt.savefig("ray.png")
