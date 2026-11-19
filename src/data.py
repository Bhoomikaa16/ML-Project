"""
Data loading and preparation for the flotation plant dataset.

Raw data: "Quality Prediction in a Mining Process" (iron ore flotation plant, Brazil,
March-September 2017). Public domain (CC0). Mirrored on OpenML as dataset 43311.
"""
import io
import os
import urllib.request

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_PATH = os.path.join(ROOT, "data", "raw", "mining_process.arff")
HOURLY_PATH = os.path.join(ROOT, "data", "processed", "flotation_hourly.csv")
FIG_DIR = os.path.join(ROOT, "figures")
RES_DIR = os.path.join(ROOT, "results")

DATA_URL = ("https://www.openml.org/data/v1/download/22102136/"
            "Quality-Prediction-in-a-Mining-Process.arff")

TARGET = "silica_conc"          # % silica in the final iron concentrate (lab, hourly)
OFF_SPEC_LIMIT = 3.0            # silica above this (%) is treated as off-spec
START = "2017-03-29 12:00"      # first hour after the 13-day stoppage in March
TRAIN_FRACTION = 0.70           # first 70 % of hours for training, last 30 % for testing

# short names, easier to read in plots and tables
RENAME = {
    "%_Iron_Feed": "iron_feed",
    "%_Silica_Feed": "silica_feed",
    "Starch_Flow": "starch_flow",
    "Amina_Flow": "amina_flow",
    "Ore_Pulp_Flow": "pulp_flow",
    "Ore_Pulp_pH": "pulp_pH",
    "Ore_Pulp_Density": "pulp_density",
    **{f"Flotation_Column_0{i}_Air_Flow": f"air_col{i}" for i in range(1, 8)},
    **{f"Flotation_Column_0{i}_Level": f"level_col{i}" for i in range(1, 8)},
    "%_Iron_Concentrate": "iron_conc",
    "%_Silica_Concentrate": "silica_conc",
}

PROCESS_VARS = (["iron_feed", "silica_feed", "starch_flow", "amina_flow",
                 "pulp_flow", "pulp_pH", "pulp_density"]
                + [f"air_col{i}" for i in range(1, 8)]
                + [f"level_col{i}" for i in range(1, 8)])

# last lab report (previous hour) - this is known to the operator at prediction time
LAB_LAGS = ["silica_prev_hr", "iron_prev_hr"]

FEATURES = PROCESS_VARS + LAB_LAGS


def download_raw(force=False):
    """Download the raw ARFF file (~185 MB) if it is not already there."""
    if os.path.exists(RAW_PATH) and not force:
        return RAW_PATH
    os.makedirs(os.path.dirname(RAW_PATH), exist_ok=True)
    print("Downloading raw data (~185 MB), this takes a few minutes...")
    urllib.request.urlretrieve(DATA_URL, RAW_PATH)
    return RAW_PATH


def load_raw():
    """Read the raw file into a DataFrame (one row every 20 seconds)."""
    download_raw()
    with open(RAW_PATH, encoding="utf-8") as f:
        lines = f.readlines()
    cols = [l.split(" ", 2)[1].strip('"') for l in lines if l.startswith("@ATTRIBUTE")]
    start = next(i for i, l in enumerate(lines) if l.strip() == "@DATA") + 1
    # numbers in the original file use a comma as the decimal separator (Brazilian format)
    df = pd.read_csv(io.StringIO("".join(lines[start:])), header=None, names=cols,
                     quotechar="'", decimal=",")
    df["date"] = pd.to_datetime(df["date"])
    return df.rename(columns=RENAME)


def make_hourly(raw):
    """Average the 20-second readings to one row per hour and add the lab lag features."""
    hourly = raw.groupby("date").mean()
    hourly = hourly[hourly.index >= START].copy()
    hourly["silica_prev_hr"] = hourly["silica_conc"].shift(1)
    hourly["iron_prev_hr"] = hourly["iron_conc"].shift(1)
    hourly = hourly.dropna()
    hourly["off_spec"] = (hourly[TARGET] > OFF_SPEC_LIMIT).astype(int)
    return hourly


def load_hourly():
    """Load the processed hourly table (created by notebook 01)."""
    if not os.path.exists(HOURLY_PATH):
        hourly = make_hourly(load_raw())
        os.makedirs(os.path.dirname(HOURLY_PATH), exist_ok=True)
        hourly.to_csv(HOURLY_PATH)
    return pd.read_csv(HOURLY_PATH, index_col="date", parse_dates=True)


def time_split(df):
    """Chronological split: no shuffling, the test period comes after the training period."""
    cut = int(len(df) * TRAIN_FRACTION)
    return df.iloc[:cut], df.iloc[cut:]
