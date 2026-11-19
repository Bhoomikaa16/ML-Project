# Bhoomi - Predicting Silica Impurity in an Iron Ore Flotation Plant

Course project for **AI-ML in Chemical Engineering**.

We use six months of real operating data from an iron ore **froth flotation** plant to:

1. **predict the % silica** (the main impurity) in the final iron ore concentrate - *regression*
2. **detect off-spec hours** (silica above 3 %) - *classification*
3. **find the plant's operating modes** without labels - *PCA and K-Means*

The plant lab measures silica only once every hour, and the result comes late. A model that estimates it from
the process sensors and the last lab result can warn the operators earlier.

## Methods covered

| Topic | Where |
|---|---|
| Data preprocessing (cleaning, resampling, leakage check, time-based split, scaling) | `01_data_preprocessing_eda` |
| Multiple linear regression (normal equation) | `02_regression` |
| Gradient descent written from scratch | `02_regression` |
| Regularization - Ridge and Lasso, with time-series cross-validation | `02_regression` |
| Random forest regression | `02_regression` |
| Logistic regression, KNN, Naive Bayes, SVM, Decision tree, Random forest | `03_classification` |
| PCA (scree plot, loadings, principal component regression) | `04_pca_kmeans_neural_network` |
| K-Means clustering (elbow, silhouette, cluster profiles) | `04_pca_kmeans_neural_network` |
| Neural network with TensorFlow / Keras (overfitting vs L2 + dropout) | `04_pca_kmeans_neural_network` |

## Dataset

**Quality Prediction in a Mining Process** - real data from an iron ore flotation plant in Brazil,
10 March to 9 September 2017. 737,453 rows, 24 columns. Licence: CC0 (public domain).

- Original: Kaggle, `edumagalhaes/quality-prediction-in-a-mining-process`
- Mirror used here: [OpenML dataset 43311](https://www.openml.org/d/43311)

The raw file is about 185 MB, so it is **not** stored in this repository. It is downloaded automatically the
first time notebook 01 runs (or run `python -m src.download` yourself). The cleaned hourly table
(`data/processed/flotation_hourly.csv`, 3,947 rows) is included, so notebooks 02-04 work without the raw file.

| Group | Columns |
|---|---|
| Feed quality (lab, hourly) | % iron feed, % silica feed |
| Reagents | starch flow, amina flow |
| Pulp | ore pulp flow, pH, density |
| Flotation columns 1-7 | air flow and level of each column |
| Concentrate (lab, hourly) | % iron concentrate, **% silica concentrate (target)** |

## Main results (test period: 22 July - 9 September 2017)

**Regression - % silica**

| Model | R² | RMSE (% silica) |
|---|---|---|
| Baseline: same as last hour | 0.608 | 0.711 |
| MLR - plant sensors only | -0.126 | 1.204 |
| MLR - last lab result only | 0.646 | 0.675 |
| MLR - all 23 inputs | 0.617 | 0.702 |
| Ridge | 0.619 | 0.700 |
| **Lasso** | **0.639** | **0.681** |
| Random forest | 0.576 | 0.739 |
| Neural network (Keras, L2 + dropout) | 0.605 | 0.713 |

**Classification - off-spec hour (silica > 3 %)**

| Model | Accuracy | Recall | Precision | F1 | ROC-AUC |
|---|---|---|---|---|---|
| **Logistic regression** | 0.868 | 0.830 | 0.685 | **0.751** | **0.906** |
| Random forest | 0.863 | 0.809 | 0.680 | 0.739 | 0.895 |
| Naive Bayes | 0.863 | 0.799 | 0.683 | 0.736 | 0.881 |
| SVM (RBF) | 0.830 | 0.845 | 0.604 | 0.704 | 0.894 |
| Decision tree | 0.821 | 0.809 | 0.592 | 0.684 | 0.874 |
| KNN | 0.821 | 0.392 | 0.735 | 0.512 | 0.790 |

**Key findings**

- The previous-hour lab result is by far the most useful input. The plant sensors on their own predict
  silica poorly in a new time period.
- Simple, regularized linear models (Lasso, logistic regression) beat Random Forest and the neural network.
- A random train/test split would have made the results look much better than they really are
  (Random Forest R² 0.33 with a random split vs 0.12 with a time split) - so we split by time.
- K-Means (without using silica) finds three operating modes. The mode where the air in columns 1-3 is cut to
  about 240 Nm³/h has 34 % off-spec hours against 22 % in normal operation - consistent with reverse flotation,
  where air bubbles carry the silica out.

## Project structure

```
bhoomi/
├── notebooks/
│   ├── 01_data_preprocessing_eda.ipynb      # cleaning, hourly resampling, EDA, split, scaling
│   ├── 02_regression.ipynb                  # MLR, gradient descent, Ridge, Lasso, RF
│   ├── 03_classification.ipynb              # 6 classifiers for off-spec detection
│   └── 04_pca_kmeans_neural_network.ipynb   # PCA, K-Means, Keras network
├── src/
│   ├── data.py          # download, loading, hourly table, feature lists, time split
│   ├── download.py      # download the raw data only
│   └── plot_style.py    # common plot settings
├── data/
│   ├── raw/             # raw file goes here (downloaded, not in git)
│   └── processed/flotation_hourly.csv
├── figures/             # all figures, saved by the notebooks
├── results/             # result tables (CSV), saved by the notebooks
├── run_all.py           # runs the four notebooks in order
└── requirements.txt
```

## How to run

**1. Get the code**

```bash
git clone https://github.com/<your-username>/bhoomi.git
cd bhoomi
```

**2. Create a virtual environment and install the packages** (Python 3.10 - 3.13)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

**3. Run the notebooks**

Open them one by one in Jupyter (run them in order 01 -> 04):

```bash
jupyter notebook notebooks/
```

or run all four from the command line (about 5 minutes, most of it the neural network):

```bash
python run_all.py
```

Notebook 01 downloads the raw data (~185 MB) the first time. If you only want notebooks 02-04, you can skip it -
they use `data/processed/flotation_hourly.csv`, which is already in the repository.

**Google Colab:** upload the repository (or clone it in a cell with `!git clone ...`), run
`!pip install -r requirements.txt`, then open the notebooks from the `notebooks/` folder.

## Notes

- All results use a fixed random seed (42), so re-running gives the same numbers. The neural network can vary
  slightly between machines (we report its spread over 5 seeds in notebook 04).
- TensorFlow runs on the CPU here; no GPU is needed.

## Reference

- Dataset: E. Magalhães Oliveira, *Quality Prediction in a Mining Process*, Kaggle (2017), CC0.
