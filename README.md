# 🌍 COVID-19 Global Vaccination Analysis & Forecasting

An interactive dashboard for epidemiological data analysis, featuring Exploratory Data Analysis (EDA) and time-series forecasting of the global COVID-19 vaccination rollout. Built using Streamlit, Plotly, and Statsmodels.

![Dashboard Preview](https://img.shields.io/badge/Status-Active-success)
![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 📌 Features

*   **📊 Strategic EDA Visualizations**: Interactive rankings and visualizations covering absolute volume leaders, per-capita coverage, and global trends.
*   **🔮 SARIMA Time-Series Forecasting**: Generates a dynamic 30-day (configurable) trajectory forecast with 90% confidence intervals for selected countries, taking into account weekly seasonality.
*   **⚔️ Cross-Country Comparison**: Compare vaccination rollout dynamics (daily doses, total doses, fully vaccinated percentages) across up to 6 different nations.
*   **📋 Interactive Data Explorer**: Filter, inspect, and download cleaned, subsetted data directly from the dashboard.
*   **🧬 Vaccine Portfolio Insights**: Analyze the widespread adoption of different vaccine combinations globally.

## 🏗️ Technology Stack

*   **Frontend/App Framework**: `streamlit`
*   **Data Processing**: `pandas`, `numpy`
*   **Data Visualization**: `plotly`
*   **Time-Series Modeling**: `statsmodels` (SARIMA)

## 📥 Dataset Requirement

The dashboard relies on the **COVID-19 World Vaccination Progress** dataset by Gabriel Preda on Kaggle.

1.  Download the dataset here: [COVID-19 World Vaccination Progress (Kaggle)](https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress)
2.  Save `country_vaccinations.csv` locally. You will upload this directly into the dashboard sidebar when running the app.

## 🚀 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/sehaan-1/covid-vaccination-analysis.git
    cd covid-vaccination-analysis
    ```

2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 🛠️ Usage

1.  Launch the application using the command above. It will open automatically in your default web browser (usually at `http://localhost:8501`).
2.  In the sidebar, click **"Browse files"** to upload your downloaded `country_vaccinations.csv`.
3.  Use the sidebar controls to:
    *   Select specific countries for forecasting.
    *   Adjust the "Top N" countries for charts.
    *   Set the forecast horizon (days).
    *   Change the application's color palette.
4.  Navigate between the different tabs to explore rankings, global trends, SARIMA forecasts, cross-country comparisons, and the raw data explorer.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
