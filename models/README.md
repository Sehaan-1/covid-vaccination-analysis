# 🤖 Models Directory

This directory is reserved for serialised model artefacts. Trained SARIMA model files (`.pkl`, `.joblib`) are **excluded from version control** per `.gitignore` — they are rebuilt on demand by the dashboard.

## How SARIMA Forecasting Works

The dashboard trains a **SARIMA(2,1,2)×(1,1,1,7)** model on-the-fly using `statsmodels` when a user selects a country in the **Forecasting** tab.

### Model Configuration

| Parameter | Value | Meaning |
|---|---|---|
| `p` | 2 | Autoregressive order |
| `d` | 1 | Differencing order |
| `q` | 2 | Moving average order |
| `P` | 1 | Seasonal autoregressive order |
| `D` | 1 | Seasonal differencing order |
| `Q` | 1 | Seasonal moving average order |
| `s` | 7 | Seasonal period (weekly cycle) |

### Why `s=7`?

Vaccination data has a strong **weekly seasonality** — fewer doses are typically reported on weekends due to reduced activity at clinics and reporting delays. The model captures this pattern explicitly.

### Preprocessing Before Fitting

1.  Missing daily values are filled via linear interpolation.
2.  Values are clipped to `≥ 0` (no negative doses).
3.  A **7-day rolling mean** is applied to smooth noise before fitting.

### Output

*   **Point forecast**: Mean predicted daily vaccinations for the selected horizon.
*   **90% confidence intervals**: Computed via `get_forecast().conf_int(alpha=0.10)`.
*   Results are clipped to `≥ 0` to prevent negative forecast values.
