from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from common.bootstrap import project_root


@dataclass(frozen=True)
class FavoritaSeriesConfig:
    store_nbr: int = 1
    family: str = "BEVERAGES"
    test_days: int = 90
    season_length: int = 7


def favorita_train_path() -> Path:
    return project_root() / "dataset" / "raw" / "train.csv"


def load_store_family_series(
    csv_path: Path | None = None,
    *,
    store_nbr: int = 1,
    family: str = "BEVERAGES",
) -> pd.DataFrame:
    """Load a single daily series from Favorita for one store and family.

    The output always has one row per calendar day and the following columns:
    - `ds`: timestamp
    - `y`: target sales
    - `onpromotion`: exogenous signal kept for Prophet
    """

    dataset_path = csv_path or favorita_train_path()
    usecols = ["date", "store_nbr", "family", "sales", "onpromotion"]
    frame = pd.read_csv(dataset_path, usecols=usecols, parse_dates=["date"])
    mask = (frame["store_nbr"] == store_nbr) & (frame["family"] == family)
    filtered = (
        frame.loc[mask, ["date", "sales", "onpromotion"]]
        .sort_values("date")
        .rename(columns={"date": "ds", "sales": "y"})
    )
    full_index = pd.date_range(filtered["ds"].min(), filtered["ds"].max(), freq="D")
    dense = (
        filtered.set_index("ds")
        .reindex(full_index)
        .rename_axis("ds")
        .reset_index()
        .rename(columns={"index": "ds"})
    )
    dense["y"] = dense["y"].fillna(0.0).astype(float)
    dense["onpromotion"] = dense["onpromotion"].fillna(0.0).astype(float)
    return dense


def temporal_train_test_split(
    frame: pd.DataFrame,
    *,
    test_days: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if test_days <= 0:
        raise ValueError("test_days must be positive")
    if len(frame) <= test_days:
        raise ValueError("test_days must be smaller than the series length")
    train = frame.iloc[:-test_days].reset_index(drop=True)
    test = frame.iloc[-test_days:].reset_index(drop=True)
    return train, test

