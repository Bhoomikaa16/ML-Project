"""Common plot settings so all figures in the report look the same."""
import os

import matplotlib.pyplot as plt

from src.data import FIG_DIR

COLORS = {"main": "#1f4e79", "accent": "#c55a11", "good": "#548235",
          "grey": "#7f7f7f", "light": "#bdd7ee"}


def setup():
    plt.rcParams.update({
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "font.size": 10,
        "axes.titlesize": 11,
        "axes.labelsize": 10,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "figure.autolayout": True,
    })


def save(fig, name):
    os.makedirs(FIG_DIR, exist_ok=True)
    fig.savefig(os.path.join(FIG_DIR, name + ".png"), bbox_inches="tight")
