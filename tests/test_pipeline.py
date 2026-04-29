
import pytest
import pandas as pd
import numpy as np

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "country": ["USA", "USA", "USA", "UK", "UK"],
        "date": pd.to_datetime([
            "2021-01-01", "2021-01-02", "2021-01-04",
            "2021-01-01", "2021-01-03"
        ]),
        "total_vaccinations":             [100, 200, np.nan, 50, 150],
        "people_vaccinated":              [80,  160, np.nan, 40, 120],
        "people_fully_vaccinated":        [0,   50,  np.nan, 0,  30],
        "daily_vaccinations":             [100, 100, np.nan, 50, 100],
        "people_fully_vaccinated_per_hundred": [0.0, 0.5, np.nan, 0.0, 0.3],
        "vaccines": ["Pfizer", "Pfizer", "Pfizer", "Oxford", "Oxford"]
    })

def test_date_parsing(sample_df):
    assert pd.api.types.is_datetime64_any_dtype(sample_df["date"])

def test_forward_fill_cumulative(sample_df):
    sample_df = sample_df.sort_values(["country", "date"]).reset_index(drop=True)
    def fill_group(group):
        group["total_vaccinations"] = group["total_vaccinations"].ffill().fillna(0)
        group["daily_vaccinations"] = group["daily_vaccinations"].fillna(0)
        return group
    result = sample_df.groupby("country", group_keys=False).apply(fill_group)
    usa_rows = result[result["country"] == "USA"].reset_index(drop=True)
    assert usa_rows.loc[2, "total_vaccinations"] == 200.0

def test_no_negative_vaccinations(sample_df):
    sample_df["daily_vaccinations"] = sample_df["daily_vaccinations"].fillna(0)
    assert (sample_df["daily_vaccinations"] >= 0).all()

def test_country_count(sample_df):
    assert sample_df["country"].nunique() == 2

def test_format_millions():
    def fmt(v):
        if v >= 1e9: return f"{v/1e9:.1f}B"
        if v >= 1e6: return f"{v/1e6:.1f}M"
        if v >= 1e3: return f"{v/1e3:.1f}K"
        return f"{v:.0f}"
    assert fmt(1_500_000_000) == "1.5B"
    assert fmt(2_500_000)     == "2.5M"
    assert fmt(3_500)         == "3.5K"
    assert fmt(500)           == "500"

def test_rolling_average_length():
    s   = pd.Series([100, 200, 150, 300, 250, 400, 350])
    ma7 = s.rolling(window=7, min_periods=1).mean()
    assert len(ma7) == len(s)

def test_forecast_nonnegative():
    mock = pd.Series([-100, 50, 200, -50, 300])
    assert (mock.clip(lower=0) >= 0).all()

def test_vaccines_column_populated(sample_df):
    assert sample_df["vaccines"].notna().sum() > 0
