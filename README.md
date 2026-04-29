# 🌍 COVID-19 Global Vaccination Analysis & SARIMA Forecasting

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.25%2B-FF4B4B?logo=streamlit&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.11%2B-3F4F75?logo=plotly&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

**An interactive epidemiological dashboard with strategic EDA and SARIMA time-series forecasting, built on the WHO-sourced COVID-19 World Vaccination dataset.**

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🏆 **Country Rankings** | Top-N countries by absolute dose count and per-capita coverage, with WHO 70% herd-immunity threshold line |
| 📈 **Global Trend** | Worldwide daily vaccinations with 7-day and 30-day moving averages, peak annotation, and country-level breakdown |
| 🔮 **SARIMA Forecasting** | On-demand `SARIMA(2,1,2)×(1,1,1,7)` model with 90% confidence intervals and CSV export |
| ⚔️ **Country Comparison** | Side-by-side comparison of up to 6 countries across daily doses, cumulative doses, and fully vaccinated % |
| 🧬 **Vaccine Portfolio** | Horizontal bar chart of the most widely adopted vaccine combinations across countries |
| 📋 **Data Explorer** | Filterable, downloadable data table with descriptive statistics |

---

## 🖥️ Dashboard Preview

> Upload `country_vaccinations.csv` from Kaggle to unlock all visualisations.

**Tabs available after upload:**
- **Rankings** — Absolute and per-capita leaders, vaccine portfolio adoption
- **Global Trend** — Worldwide vaccination pace over time
- **Forecasting** — Country-specific SARIMA forecast with confidence bands
- **Comparison** — Multi-country rollout comparison
- **Data Explorer** — Raw data viewer and downloader

---

## 🏗️ Technology Stack

| Library | Version | Role |
|---|---|---|
| `streamlit` | ≥ 1.25 | Interactive web application |
| `pandas` | ≥ 1.5 | Data loading and cleaning |
| `numpy` | ≥ 1.23 | Numerical operations |
| `plotly` | ≥ 5.11 | Interactive visualisations |
| `statsmodels` | ≥ 0.13.5 | SARIMA time-series modelling |
| `scikit-learn` | ≥ 1.1 | Error metric calculations |
| `scipy` | ≥ 1.9 | Statistical utilities |

---

## 📥 Dataset

The dashboard uses the **[COVID-19 World Vaccination Progress](https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress)** dataset by **Gabriel Preda** on Kaggle (~86,000 rows, 15 columns, 200+ countries).

The dataset is not stored in this repository — see [`data/README.md`](data/README.md) for the full schema and download instructions.

---

## 🚀 Quickstart

```bash
# 1. Clone the repo
git clone https://github.com/sehaan-1/covid-vaccination-analysis.git
cd covid-vaccination-analysis

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the dashboard
streamlit run app.py
```

Then open [http://localhost:8501](http://localhost:8501) in your browser and upload your `country_vaccinations.csv`.

---

## 🗂️ Repository Structure

```
covid-vaccination-analysis/
│
├── app.py                    # Main Streamlit application (all tabs & charts)
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml           # Streamlit theme and server settings
│
├── data/
│   └── README.md             # Dataset schema and download instructions
│
├── models/
│   └── README.md             # SARIMA model documentation
│
├── tests/
│   └── test_pipeline.py      # pytest unit tests for data pipeline
│
├── CONTRIBUTING.md           # How to contribute
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

## 🧪 Running Tests

```bash
pip install pytest
pytest tests/ -v
```

The test suite covers: date parsing, forward-fill logic, non-negative vaccination values, country counts, rolling averages, and the forecast non-negativity clip.

---

## 📈 SARIMA Model Details

The forecasting tab trains a `SARIMA(2,1,2)×(1,1,1,7)` model per selected country:

- **Weekly seasonality** (`s=7`) captures the real-world pattern of reduced weekend reporting.
- **7-day rolling average** is applied as pre-processing to reduce noise before fitting.
- **90% confidence intervals** widen naturally at longer horizons, reflecting genuine uncertainty.
- See [`models/README.md`](models/README.md) for a full breakdown of parameters and preprocessing.

---

## 🤝 Contributing

Contributions are welcome! Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) first.

---

## 📜 License

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for details.

---

<div align="center">
  Built with ❤️ using Streamlit &amp; Statsmodels &nbsp;|&nbsp; Data: WHO via Kaggle
</div>
