import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------
# Einstein radius (radian)
# --------------------------------------------
thetaE = 0.18


# --------------------------------------------
# Mercator -> Sphere
# --------------------------------------------
def mercator_to_sphere(lon, v):
    lat = 2 * np.arctan(np.exp(v)) - np.pi / 2

    x = np.cos(lat) * np.cos(lon)
    y = np.cos(lat) * np.sin(lon)
    z = np.sin(lat)

    return x, y, z


# --------------------------------------------
# Sphere -> Mercator
# --------------------------------------------
def sphere_to_mercator(x, y, z):

    lon = np.arctan2(y, x)
    lat = np.arcsin(np.clip(z, -1, 1))

    v = np.log(np.tan(np.pi / 4 + lat / 2))

    return lon, v


# --------------------------------------------
# Point-mass lens
# lens located along +x direction
# --------------------------------------------
def lens(x, y, z):

    # only rays looking toward +x
    if np.any(x <= 0):
        return np.nan, np.nan, np.nan

    tx = y / x
    ty = z / x

    r2 = tx**2 + ty**2 + 1e-10

    ax = thetaE**2 * tx / r2
    ay = thetaE**2 * ty / r2

    bx = tx - ax
    by = ty - ay

    n = np.sqrt(1 + bx**2 + by**2)

    return 1 / n, bx / n, by / n


# --------------------------------------------
# full mapping
# --------------------------------------------
def map_point(lon, v):

    x, y, z = mercator_to_sphere(lon, v)

    x, y, z = lens(x, y, z)

    if np.isnan(x):
        return np.nan, np.nan

    return sphere_to_mercator(x, y, z)


# ============================================
# Plot
# ============================================

fig, ax = plt.subplots(figsize=(10, 8))

# longitude lines
for lon0 in np.linspace(-1.2, 1.2, 17):

    vv = np.linspace(-1.2, 1.2, 500)

    lon = np.full_like(vv, lon0)

    # original
    ax.plot(lon, vv, color="0.8", lw=1)

    # lensed
    L = []
    V = []

    for l, v in zip(lon, vv):
        l2, v2 = map_point(l, v)
        L.append(l2)
        V.append(v2)

    ax.plot(L, V, "C0", lw=2)

# latitude lines
for v0 in np.linspace(-1.2, 1.2, 17):

    lon = np.linspace(-1.2, 1.2, 500)
    vv = np.full_like(lon, v0)

    ax.plot(lon, vv, color="0.8", lw=1)

    L = []
    V = []

    for l, v in zip(lon, vv):
        l2, v2 = map_point(l, v)
        L.append(l2)
        V.append(v2)

    ax.plot(L, V, "C0", lw=2)

ax.set_xlim(-1.3, 1.3)
ax.set_ylim(-1.3, 1.3)

ax.set_xlabel("Longitude (Mercator)")
ax.set_ylabel("Mercator y")
ax.set_aspect("equal")
plt.tight_layout()
# plt.show()
plt.savefig("out.png")
