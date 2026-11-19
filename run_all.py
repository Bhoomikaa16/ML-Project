"""Run all four notebooks in order and save their outputs in place.

Usage:  python run_all.py
"""
import os
import subprocess
import sys
import time

NOTEBOOKS = [
    "01_data_preprocessing_eda.ipynb",
    "02_regression.ipynb",
    "03_classification.ipynb",
    "04_pca_kmeans_neural_network.ipynb",
]

here = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notebooks")

for nb in NOTEBOOKS:
    start = time.time()
    print(f"Running {nb} ...", flush=True)
    subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
                    "--inplace", "--ExecutePreprocessor.timeout=1800", nb], cwd=here, check=True)
    print(f"  done in {time.time() - start:.0f} s")

print("All notebooks finished. Figures are in figures/, result tables in results/.")
