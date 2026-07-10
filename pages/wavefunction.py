import io

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

import streamlit as st

from sympy import (
    symbols,
    sympify,
    lambdify,
    Integral,
    integrate,
    conjugate,
    oo,
    sqrt,
    sinc,
    cos,
    exp,
    pi,
)
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
)
from scipy.integrate import quad
import numpy as np

st.set_page_config(page_title="Function Plotter", layout="wide")

st.title("Function Plotter")

# -------------------------
# Sidebar
# -------------------------

x = symbols("x")

with st.sidebar:
    st.header("Wave Function Setting")

    # expr_str = st.text_input("y =", value="sin(x) + 0.3*cos(5*x)")

    kind = st.selectbox(
        "Function",
        [
            "Gaussian",
            "Double slit",
        ],
    )
    if kind == "Gaussian":
        log10sigma = st.slider("log10sigma", -2.0, 2.0, 0.0)
        mu = st.slider("mu", -5.0, 5.0, 0.0)
        expr = (1 / (sqrt(2 * pi) * 10**log10sigma)) * exp(
            -((x - mu) ** 2) / (2 * 10 ** (log10sigma * 2))
        )
    elif kind == "Double slit":
        alpha = st.slider("alpha", 0.0, 20.0, 1.0)
        if -1.0 <= alpha <= 1.0:
            I = 1.0 - sqrt(alpha * alpha) / 2
        else:
            I = 1 / 2
        expr = sqrt(I) * sinc(x) * cos(pi * alpha * x)

    xmin = st.number_input("xmin", value=-np.pi)
    xmax = st.number_input("xmax", value=np.pi)
    n = st.slider("samples", 1, 100, 20) * 100
    linewidth = st.slider("linewidth", 0.2, 5.0, 1.5)


# -------------------------
# Parse function
# -------------------------

f = lambdify(x, expr, "numpy")
g = lambdify(x, expr * conjugate(expr), "numpy")

xx = np.linspace(xmin, xmax, n)
phi = f(xx)
rho = g(xx)

# transformations = standard_transformations + (implicit_multiplication_application,)

# try:
# expr = parse_expr(expr_str, transformations=transformations)
# I = Integral(expr * conjugate(expr), (x, -oo, oo)).doit()
# I = (1 / I if I > 1e-16 else I) if I.is_finite else 0.0

# except Exception as e:
#    st.error(e)
#    st.stop()

# -------------------------
# Plot
# -------------------------

fig, ax = plt.subplots(figsize=(6, 4))

ymax = np.max(np.abs(phi)) * 1.2
ymin = -ymax

dy = ymax - ymin
dx = xx[1] - xx[0]

for x, c in zip(xx, rho / np.max(rho)):
    ax.add_patch(
        Rectangle(
            (x - dx / 2, ymin),  # 左下
            dx,  # 幅
            dy,  # 高さ
            facecolor=(0, 0, c),
            edgecolor="none",
            linewidth=0,
            zorder=0,
        )
    )

ax.plot(xx, phi, lw=linewidth, c="yellow")

ax.set_xlabel("x")
ax.set_ylabel("phi")
ax.set_xlim([xmin, xmax])
ax.set_ylim([ymin, ymax])

st.pyplot(fig)

# -------------------------
# EPS download
# -------------------------

eps = io.BytesIO()

fig.savefig(eps, format="eps", bbox_inches="tight")

eps.seek(0)

st.download_button(
    "Download EPS",
    data=eps,
    file_name="figure.eps",
    mime="application/postscript",
)
