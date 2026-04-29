# 📂 Data Directory

This directory holds the raw dataset used by the dashboard. The CSV file is **excluded from version control** (see `.gitignore`) due to its size (~17 MB), so you must download it manually.

## 📥 How to Get the Data

1.  Go to the Kaggle dataset page: **[COVID-19 World Vaccination Progress](https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress)**
2.  Download `country_vaccinations.csv`
3.  You do **not** need to place it here — simply upload it via the dashboard sidebar when the app is running.

## 📊 Dataset Schema

The dashboard expects a CSV with the following columns:

| Column | Type | Description |
|---|---|---|
| `country` | `str` | Country name |
| `iso_code` | `str` | ISO 3166-1 alpha-3 country code |
| `date` | `date` | Reporting date (YYYY-MM-DD) |
| `total_vaccinations` | `float` | Cumulative total vaccine doses administered |
| `people_vaccinated` | `float` | Cumulative number of people with at least 1 dose |
| `people_fully_vaccinated` | `float` | Cumulative number of people fully vaccinated |
| `daily_vaccinations_raw` | `float` | New doses reported that day (raw, may have gaps) |
| `daily_vaccinations` | `float` | New doses (7-day smoothed estimate) |
| `total_vaccinations_per_hundred` | `float` | Total doses per 100 population |
| `people_vaccinated_per_hundred` | `float` | People (≥1 dose) per 100 population |
| `people_fully_vaccinated_per_hundred` | `float` | Fully vaccinated people per 100 population |
| `daily_vaccinations_per_million` | `float` | Daily doses per 1,000,000 population |
| `vaccines` | `str` | Comma-separated list of vaccine brands in use |
| `source_name` | `str` | Data source name (dropped during cleaning) |
| `source_website` | `str` | Data source URL (dropped during cleaning) |

## 🧹 Data Cleaning Notes

The `load_and_clean()` function in `app.py` performs the following steps automatically on upload:

1.  **Encoding detection** — handles UTF-8, UTF-8 BOM, Latin-1, and CP1252.
2.  **Column normalisation** — strips whitespace and lowercases all column names.
3.  **Date parsing** — converts the `date` column to `datetime64`.
4.  **Forward-fill** — fills gaps in cumulative columns per country using the last known value.
5.  **Zero-fill** — fills missing daily values with 0.
6.  **Metadata removal** — drops `source_name` and `source_website` columns.
