import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import io
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="COVID-19 Vaccination Analysis",
    page_icon="💉",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1a1a2e;
        text-align: center;
        padding: 1rem 0 0.5rem 0;
    }
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1rem;
        margin-bottom: 1.5rem;
    }
    .insight-box {
        background-color: #f0f7ff;
        border-left: 4px solid #3b528b;
        padding: 1rem 1.5rem;
        border-radius: 0 8px 8px 0;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────
def format_millions(value):
    try:
        if pd.isna(value):
            return 'N/A'
    except Exception:
        return 'N/A'
    if value >= 1e9:
        return f'{value / 1e9:.2f}B'
    elif value >= 1e6:
        return f'{value / 1e6:.2f}M'
    elif value >= 1e3:
        return f'{value / 1e3:.1f}K'
    return f'{value:.0f}'


def load_and_clean(file):
    file.seek(0)
    raw = file.read()

    # Try multiple encodings — utf-8-sig strips the BOM character that
    # commonly prefixes CSV files saved from Excel / Windows.
    for enc in ['utf-8-sig', 'utf-8', 'latin-1']:
        try:
            df = pd.read_csv(
                io.BytesIO(raw),
                low_memory=False,
                header=0,
                index_col=None,           # Prevent first column becoming index
                encoding=enc
            )
            break
        except Exception:
            continue
    else:
        st.error("Could not decode the CSV with any supported encoding.")
        st.stop()

    # Aggressive column name cleaning
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace(r'[^a-z0-9_]', '', regex=True)   # Remove any weird characters
    )

    # Fix if first column is unnamed (very common with this dataset)
    if df.columns[0] in ['', 'unnamed', 'unnamed0', 'unnamed_0']:
        df = df.iloc[:, 1:].reset_index(drop=True)
        # Re-clean column names after dropping
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(' ', '_')
            .str.replace(r'[^a-z0-9_]', '', regex=True)
        )

    # Robust country column mapping — try many common alternatives
    if 'country' not in df.columns:
        alias_map = {
            'location': 'country',
            'country_region': 'country',
            'countryregion': 'country',
            'name': 'country',
        }
        for alias, target in alias_map.items():
            if alias in df.columns:
                df = df.rename(columns={alias: target})
                break

    # Last-resort: find any column whose name *contains* 'country'
    if 'country' not in df.columns:
        country_cols = [c for c in df.columns if 'country' in c]
        if country_cols:
            df = df.rename(columns={country_cols[0]: 'country'})

    # Final validation
    if 'country' not in df.columns:
        st.error(f"'country' column is still missing after cleaning.\n\n"
                f"Columns found: {df.columns.tolist()}\n\n"
                f"Please make sure you're uploading `country_vaccinations.csv` "
                f"from the Kaggle dataset (not the manufacturer version).")
        st.stop()

    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df = df.dropna(subset=['date']).sort_values(['country', 'date']).reset_index(drop=True)

    # Add missing columns with NaN instead of 0 (better for robustness)
    for col in ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
                'daily_vaccinations', 'total_vaccinations_per_hundred',
                'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred',
                'daily_vaccinations_per_million', 'vaccines']:
        if col not in df.columns:
            df[col] = np.nan

    # Forward fill cumulative columns per country
    cum_cols = [
        'total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated',
        'total_vaccinations_per_hundred', 'people_vaccinated_per_hundred',
        'people_fully_vaccinated_per_hundred'
    ]

    # Forward-fill cumulative columns and fill daily with 0, per country.
    # Use .transform() instead of .apply() to avoid pandas 3.x dropping the
    # grouping column from the result.
    for c in cum_cols:
        df[c] = df.groupby('country')[c].transform(lambda x: x.ffill().fillna(0))
    df['daily_vaccinations'] = df.groupby('country')['daily_vaccinations'].transform(
        lambda x: x.fillna(0)
    )
    return df.reset_index(drop=True)


# ── Header ────────────────────────────────────────────────────
st.markdown(
    "<div class='main-header'>"
    "🌍 COVID-19 Global Vaccination Analysis &amp; SARIMA Forecasting"
    "</div>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='sub-header'>"
    "Epidemiological data analysis · Time-series forecasting · Strategic insights"
    "</div>",
    unsafe_allow_html=True
)
st.markdown("---")

# ── Sidebar (always visible) ──────────────────────────────────
with st.sidebar:
    st.title("⚙️ Dashboard Controls")
    st.markdown("---")
    uploaded_file = st.file_uploader(
        "📂 Upload Dataset",
        type=["csv"],
        help="Upload country_vaccinations.csv from Kaggle"
    )
    st.markdown("---")
    st.markdown("### 📥 Get the Dataset")
    st.markdown(
        "[Download from Kaggle]"
        "(https://www.kaggle.com/datasets/gpreda/covid-world-vaccination-progress)"
    )
    st.markdown("---")
    st.markdown("### 🔗 Project Links")
    st.markdown(
        "[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)]"
        "(https://github.com/sehaan-1/covid-vaccination-analysis)"
    )
    st.markdown("---")
    st.caption("Portfolio Project · Data Science Capstone")


# ══════════════════════════════════════════════════════════════
# LANDING PAGE — no file uploaded
# ══════════════════════════════════════════════════════════════
if uploaded_file is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 👆 Upload the dataset in the sidebar to begin")
        st.markdown("")

        st.markdown("""
        <div class="insight-box">
        <strong>What this dashboard does:</strong><br><br>
        📊 &nbsp;<b>4 strategic EDA visualisations</b> — volume leaders, per-capita
        coverage, global trend, vaccine market share<br><br>
        🔮 &nbsp;<b>SARIMA time-series forecasting</b> — 30-day vaccination trajectory
        with 90% confidence intervals<br><br>
        ⚔️ &nbsp;<b>Cross-country comparison</b> — compare rollout dynamics across nations<br><br>
        📋 &nbsp;<b>Interactive data explorer</b> — filter, inspect, and download cleaned data
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")
        st.markdown("### 📌 How to Use")
        st.markdown("""
        1. **Download** the dataset from the Kaggle link in the sidebar
        2. **Upload** `country_vaccinations.csv` using the file uploader
        3. **Explore** — all charts generate automatically
        4. **Interact** — zoom, hover, filter by country, adjust forecast horizon
        """)

        st.markdown("")
        st.markdown("### 🏗️ Technical Stack")
        st.dataframe(
            pd.DataFrame({
                'Library': [
                    'pandas', 'numpy', 'statsmodels',
                    'plotly', 'streamlit', 'scikit-learn'
                ],
                'Purpose': [
                    'Data cleaning & manipulation',
                    'Numerical operations',
                    'SARIMA time-series modeling',
                    'Interactive visualisations',
                    'Web application framework',
                    'Error metrics (MAE/RMSE)'
                ]
            }),
            use_container_width=True,
            hide_index=True
        )

# ══════════════════════════════════════════════════════════════
# MAIN DASHBOARD — file uploaded
# ══════════════════════════════════════════════════════════════
else:
    with st.spinner("Reading and cleaning data..."):
        try:
            df = load_and_clean(uploaded_file)
        except Exception as e:
            st.error(f"Failed to load dataset: {e}")
            st.stop()

    if df is None or len(df) == 0:
        st.error("DataFrame is empty after loading. Check the file and re-upload.")
        st.stop()

    if 'country' not in df.columns:
        st.error(f"'country' column missing. Columns found: {df.columns.tolist()}")
        st.stop()

    # ── Sidebar controls ──────────────────────────────────────
    with st.sidebar:
        st.success(f"✅ {len(df):,} rows | {df['country'].nunique()} countries")
        st.markdown("---")
        st.markdown("### 🌍 Country Selection")

        countries = sorted(df['country'].dropna().unique().tolist())
        default_idx = countries.index('United States') if 'United States' in countries else 0
        selected_country = st.selectbox("Forecast country:", countries, index=default_idx)

        top_n = st.slider("Top N in ranking charts:", 5, 20, 10)
        forecast_days = st.slider("Forecast horizon (days):", 7, 60, 30)

        st.markdown("---")
        st.markdown("### 🎨 Chart Style")
        palette = st.selectbox("Colour palette:", ["Viridis", "Plasma", "Cividis", "Turbo"])

    # ── KPI Metrics ───────────────────────────────────────────
    st.markdown("### 📈 Global Key Metrics")

    total_doses = df.groupby('country')['total_vaccinations'].max().sum()
    peak_daily = df.groupby('date')['daily_vaccinations'].sum().max()
    days_of_data = (df['date'].max() - df['date'].min()).days
    top_country_name = df.groupby('country')['total_vaccinations'].max().idxmax()

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("🌍 Countries",     f"{df['country'].nunique():,}")
    k2.metric("💉 Total Doses",   format_millions(total_doses))
    k3.metric("📅 Peak Daily",    format_millions(peak_daily))
    k4.metric("📆 Days of Data",  f"{days_of_data:,}")
    k5.metric("🏆 Volume Leader", top_country_name)

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Rankings",
        "📈 Global Trend",
        "🔮 Forecasting",
        "⚔️ Comparison",
        "📋 Data Explorer"
    ])

    # ══════════════════════════════════════════════════════════
    # TAB 1 — RANKINGS
    # ══════════════════════════════════════════════════════════
    with tab1:
        st.markdown("### Country Vaccination Rankings")

        col_a, col_b = st.columns(2)

        with col_a:
            st.markdown("#### 💉 Absolute Volume Leaders")
            top_vol = (
                df.groupby('country')['total_vaccinations']
                .max()
                .sort_values(ascending=False)
                .head(top_n)
                .reset_index()
            )
            top_vol.columns = ['country', 'total_vaccinations']

            fig_vol = go.Figure(go.Bar(
                x=top_vol['country'],
                y=top_vol['total_vaccinations'],
                marker=dict(
                    color=top_vol['total_vaccinations'],
                    colorscale=palette,
                    showscale=False
                ),
                text=[format_millions(v) for v in top_vol['total_vaccinations']],
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Total Doses: %{text}<extra></extra>'
            ))
            fig_vol.update_layout(
                template='plotly_white',
                height=420,
                xaxis_tickangle=-30,
                yaxis_title='Total Doses Administered',
                margin=dict(t=30, b=80)
            )
            st.plotly_chart(fig_vol, use_container_width=True)
            st.caption(
                "Absolute counts reflect population size — "
                "see per-capita chart for normalised comparison."
            )

        with col_b:
            st.markdown("#### 🎯 Per-Capita Coverage Leaders")
            top_pc = (
                df.groupby('country')['people_fully_vaccinated_per_hundred']
                .max()
                .dropna()
                .sort_values(ascending=False)
                .head(top_n)
                .reset_index()
            )
            top_pc.columns = ['country', 'pct']

            if len(top_pc) == 0 or top_pc['pct'].sum() == 0:
                st.warning(
                    "Per-capita data not available in this file.\n\n"
                    "Upload `country_vaccinations.csv` (not the manufacturer file) "
                    "for full coverage metrics."
                )
            else:
                fig_pc = go.Figure(go.Bar(
                    x=top_pc['country'],
                    y=top_pc['pct'],
                    marker=dict(
                        color=top_pc['pct'],
                        colorscale=palette,
                        showscale=False
                    ),
                    text=[f"{v:.1f}%" for v in top_pc['pct']],
                    textposition='outside',
                    hovertemplate='<b>%{x}</b><br>Fully Vaccinated: %{text}<extra></extra>'
                ))
                fig_pc.add_hline(
                    y=70,
                    line_dash='dash',
                    line_color='red',
                    annotation_text='70% WHO Threshold',
                    annotation_position='top right'
                )
                fig_pc.update_layout(
                    template='plotly_white',
                    height=420,
                    xaxis_tickangle=-30,
                    yaxis_title='People Fully Vaccinated per 100',
                    margin=dict(t=30, b=80)
                )
                st.plotly_chart(fig_pc, use_container_width=True)
                st.caption(
                    "Red dashed line = approximate herd immunity threshold "
                    "referenced by WHO guidelines."
                )

        st.markdown("---")
        st.markdown("#### 🧬 Vaccine Portfolio Adoption")

        if 'vaccines' in df.columns and df['vaccines'].notna().sum() > 0:
            vaccine_per_country = (
                df.sort_values('date')
                .groupby('country')['vaccines']
                .last()
                .dropna()
                .reset_index()
            )
            vaccine_counts = (
                vaccine_per_country['vaccines']
                .value_counts()
                .head(10)
                .reset_index()
            )
            vaccine_counts.columns = ['vaccine_combination', 'country_count']
            vaccine_counts['label'] = vaccine_counts['vaccine_combination'].apply(
                lambda x: (x[:50] + '...') if len(str(x)) > 50 else x
            )

            fig_vax = go.Figure(go.Bar(
                x=vaccine_counts['country_count'][::-1],
                y=vaccine_counts['label'][::-1],
                orientation='h',
                marker=dict(
                    color=vaccine_counts['country_count'][::-1],
                    colorscale=palette,
                    showscale=False
                ),
                text=[f"{v} countries" for v in vaccine_counts['country_count'][::-1]],
                textposition='outside',
                hovertemplate='<b>%{y}</b><br>%{text}<extra></extra>'
            ))
            fig_vax.update_layout(
                template='plotly_white',
                height=430,
                xaxis_title='Number of Countries',
                margin=dict(l=10, r=130, t=20, b=20)
            )
            st.plotly_chart(fig_vax, use_container_width=True)
        else:
            st.info("Vaccine portfolio data not available in this file.")

    # ══════════════════════════════════════════════════════════
    # TAB 2 — GLOBAL TREND
    # ══════════════════════════════════════════════════════════
    with tab2:
        st.markdown("### 📈 Global Daily Vaccination Trend")

        global_daily = (
            df.groupby('date')['daily_vaccinations']
            .sum()
            .reset_index()
            .rename(columns={'daily_vaccinations': 'global_daily'})
        )
        nonzero_idx = global_daily[global_daily['global_daily'] > 0].index
        if len(nonzero_idx) > 0:
            global_daily = global_daily.loc[nonzero_idx[0]:].reset_index(drop=True)

        global_daily['ma_7d']  = global_daily['global_daily'].rolling(7,  min_periods=1).mean()
        global_daily['ma_30d'] = global_daily['global_daily'].rolling(30, min_periods=1).mean()

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=global_daily['date'],
            y=global_daily['global_daily'],
            mode='lines',
            line=dict(color='rgba(33,145,140,0.4)', width=1),
            fill='tozeroy',
            fillcolor='rgba(33,145,140,0.08)',
            name='Daily Raw',
            hovertemplate='%{x|%b %d %Y}<br>%{y:,.0f} doses<extra></extra>'
        ))
        fig_trend.add_trace(go.Scatter(
            x=global_daily['date'],
            y=global_daily['ma_7d'],
            mode='lines',
            line=dict(color='#3b528b', width=2.5),
            name='7-Day MA',
            hovertemplate='%{x|%b %d %Y}<br>7d MA: %{y:,.0f}<extra></extra>'
        ))
        fig_trend.add_trace(go.Scatter(
            x=global_daily['date'],
            y=global_daily['ma_30d'],
            mode='lines',
            line=dict(color='#fde725', width=2.5, dash='dash'),
            name='30-Day MA',
            hovertemplate='%{x|%b %d %Y}<br>30d MA: %{y:,.0f}<extra></extra>'
        ))

        if len(global_daily) > 0:
            peak_row = global_daily.loc[global_daily['global_daily'].idxmax()]
            fig_trend.add_annotation(
                x=peak_row['date'],
                y=peak_row['global_daily'],
                text=f"Peak: {format_millions(peak_row['global_daily'])}",
                showarrow=True,
                arrowhead=2,
                arrowcolor='#e63946',
                font=dict(size=11, color='#e63946'),
                bgcolor='white',
                bordercolor='#e63946',
                borderwidth=1,
                ax=50, ay=-50
            )

        fig_trend.update_layout(
            template='plotly_white',
            height=520,
            xaxis_title='Date',
            yaxis_title='Daily Vaccine Doses',
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom', y=1.02,
                xanchor='right',  x=1
            )
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        # Country-level trend
        st.markdown("---")
        st.markdown(f"#### 📍 {selected_country} — Daily Vaccination Trend")

        try:
            cdata = df[df['country'] == selected_country].copy().sort_values('date')
            if cdata.empty:
                st.warning(f"No data found for {selected_country}.")
            else:
                cdata = cdata.set_index('date')
                cts   = cdata['daily_vaccinations'].copy()

                full_r = pd.date_range(cts.index.min(), cts.index.max(), freq='D')
                cts    = cts.reindex(full_r).interpolate(method='linear').clip(lower=0)
                cma7   = cts.rolling(7,  min_periods=1).mean()
                cma30  = cts.rolling(30, min_periods=1).mean()

                fig_c = go.Figure()
                fig_c.add_trace(go.Scatter(
                    x=cts.index, y=cts.values,
                    mode='lines',
                    line=dict(color='rgba(49,104,142,0.35)', width=1),
                    fill='tozeroy',
                    fillcolor='rgba(49,104,142,0.07)',
                    name='Daily Raw'
                ))
                fig_c.add_trace(go.Scatter(
                    x=cma7.index, y=cma7.values,
                    mode='lines',
                    line=dict(color='#35b779', width=2.5),
                    name='7-Day MA'
                ))
                fig_c.add_trace(go.Scatter(
                    x=cma30.index, y=cma30.values,
                    mode='lines',
                    line=dict(color='#fde725', width=2.5, dash='dash'),
                    name='30-Day MA'
                ))
                fig_c.update_layout(
                    template='plotly_white',
                    height=420,
                    xaxis_title='Date',
                    yaxis_title='Daily Doses',
                    hovermode='x unified',
                    legend=dict(
                        orientation='h',
                        yanchor='bottom', y=1.02,
                        xanchor='right',  x=1
                    )
                )
                st.plotly_chart(fig_c, use_container_width=True)

        except Exception as e:
            st.warning(f"Could not plot trend for {selected_country}: {e}")

    # ══════════════════════════════════════════════════════════
    # TAB 3 — FORECASTING
    # ══════════════════════════════════════════════════════════
    with tab3:
        st.markdown(f"### 🔮 SARIMA Forecast — {selected_country}")
        st.info(
            f"Training SARIMA(2,1,2)×(1,1,1,7) on {selected_country} data. "
            f"Forecasting **{forecast_days} days** ahead. This takes 1–2 minutes."
        )

        run_forecast = st.button("▶️ Run Forecast", type="primary")

        if run_forecast:
            try:
                from statsmodels.tsa.statespace.sarimax import SARIMAX

                cdata = df[df['country'] == selected_country].copy()
                if cdata.empty:
                    st.error(f"No data available for {selected_country}.")
                    st.stop()

                cdata  = cdata.set_index('date').sort_index()
                ts     = cdata['daily_vaccinations'].copy()

                full_r = pd.date_range(ts.index.min(), ts.index.max(), freq='D')
                ts     = ts.reindex(full_r).interpolate(method='linear').clip(lower=0)
                ts_sm  = ts.rolling(7, min_periods=1).mean()

                if len(ts_sm) < 30:
                    st.error(
                        f"{selected_country} has fewer than 30 data points. "
                        "Please select a country with more data."
                    )
                    st.stop()

                with st.spinner(f"Fitting SARIMA model for {selected_country}..."):
                    model = SARIMAX(
                        ts_sm,
                        order=(2, 1, 2),
                        seasonal_order=(1, 1, 1, 7),
                        enforce_stationarity=False,
                        enforce_invertibility=False,
                        trend='c'
                    )
                    result = model.fit(disp=False, maxiter=150, method='lbfgs')

                fc       = result.get_forecast(steps=forecast_days)
                fc_mean  = fc.predicted_mean.clip(lower=0)
                fc_ci    = fc.conf_int(alpha=0.10).clip(lower=0)
                fc_dates = pd.date_range(
                    ts_sm.index[-1] + pd.Timedelta(days=1),
                    periods=forecast_days,
                    freq='D'
                )
                fc_mean.index = fc_dates
                fc_ci.index   = fc_dates

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("AIC",                   f"{result.aic:,.1f}")
                m2.metric("BIC",                   f"{result.bic:,.1f}")
                m3.metric(f"Day {forecast_days}",  format_millions(fc_mean.iloc[-1]))
                m4.metric("Seasonal Period",        "7 days (weekly)")

                history = ts_sm.iloc[-120:]

                fig_fc = go.Figure()
                fig_fc.add_trace(go.Scatter(
                    x=history.index, y=history.values,
                    mode='lines',
                    line=dict(color='#31688e', width=2),
                    name='Historical (7d MA)',
                    hovertemplate='%{x|%b %d %Y}<br>%{y:,.0f}<extra></extra>'
                ))
                fig_fc.add_trace(go.Scatter(
                    x=pd.concat([
                        fc_mean.index.to_series(),
                        fc_mean.index.to_series()[::-1]
                    ]),
                    y=pd.concat([fc_ci.iloc[:, 1], fc_ci.iloc[:, 0][::-1]]),
                    fill='toself',
                    fillcolor='rgba(230,57,70,0.12)',
                    line=dict(color='rgba(0,0,0,0)'),
                    name='90% Confidence Interval',
                    hoverinfo='skip'
                ))
                fig_fc.add_trace(go.Scatter(
                    x=fc_mean.index, y=fc_mean.values,
                    mode='lines',
                    line=dict(color='#e63946', width=2.5, dash='dash'),
                    name='SARIMA Forecast',
                    hovertemplate='%{x|%b %d %Y}<br>Forecast: %{y:,.0f}<extra></extra>'
                ))
                fig_fc.add_vline(
                    x=str(ts_sm.index[-1].date()),
                    line_dash='dot',
                    line_color='gray',
                    annotation_text='Forecast Start',
                    annotation_position='top left'
                )
                fig_fc.update_layout(
                    template='plotly_white',
                    height=520,
                    xaxis_title='Date',
                    yaxis_title='Daily Vaccine Doses',
                    hovermode='x unified',
                    title=dict(
                        text=(
                            f'SARIMA(2,1,2)×(1,1,1,7) — {selected_country} | '
                            f'{forecast_days}-Day Forecast'
                        ),
                        font=dict(size=13)
                    ),
                    legend=dict(
                        orientation='h',
                        yanchor='bottom', y=1.02,
                        xanchor='right',  x=1
                    )
                )
                st.plotly_chart(fig_fc, use_container_width=True)

                forecast_df = pd.DataFrame({
                    'date':       fc_dates.strftime('%Y-%m-%d'),
                    'forecast':   fc_mean.values.round(0),
                    'lower_90ci': fc_ci.iloc[:, 0].values.round(0),
                    'upper_90ci': fc_ci.iloc[:, 1].values.round(0)
                })
                st.download_button(
                    label="📥 Download Forecast CSV",
                    data=forecast_df.to_csv(index=False),
                    file_name=(
                        f"sarima_forecast_"
                        f"{selected_country.lower().replace(' ', '_')}.csv"
                    ),
                    mime='text/csv'
                )

                st.markdown("---")
                st.markdown("#### 💡 Model Insights")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("""
                    <div class="insight-box">
                    <b>Weekly Seasonality (s=7)</b><br>
                    Captures the 7-day reporting cycle caused by reduced
                    weekend data submissions from healthcare facilities.
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown("""
                    <div class="insight-box">
                    <b>90% Confidence Intervals</b><br>
                    Wider bands at longer horizons reflect genuine uncertainty
                    in vaccination campaign dynamics beyond 2–3 weeks.
                    </div>
                    """, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Forecasting failed: {e}")
                st.info(
                    "Common causes:\n"
                    "- Not enough data points for this country\n"
                    "- Try selecting a larger country with more data"
                )

        else:
            st.markdown("""
            <div class="insight-box">
            Click <b>▶️ Run Forecast</b> above to train the SARIMA model
            and generate a forecast for the selected country.
            Training takes approximately 1–2 minutes.
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════
    # TAB 4 — COMPARISON
    # ══════════════════════════════════════════════════════════
    with tab4:
        st.markdown("### ⚔️ Cross-Country Comparison")

        default_compare = [c for c in ['United States', 'United Kingdom', 'India']
                           if c in countries]
        if len(default_compare) < 2:
            default_compare = countries[:min(3, len(countries))]

        compare_countries = st.multiselect(
            "Select countries to compare (2–6 recommended):",
            options=countries,
            default=default_compare
        )

        if len(compare_countries) < 2:
            st.warning("Select at least 2 countries to compare.")
        else:
            metric_choice = st.radio(
                "Metric:",
                [
                    'daily_vaccinations',
                    'total_vaccinations',
                    'people_fully_vaccinated_per_hundred'
                ],
                format_func=lambda x: {
                    'daily_vaccinations':                  'Daily Vaccinations (7d MA)',
                    'total_vaccinations':                  'Total Vaccinations (Cumulative)',
                    'people_fully_vaccinated_per_hundred': '% Fully Vaccinated'
                }[x],
                horizontal=True
            )

            fig_cmp    = go.Figure()
            colors_cmp = px.colors.qualitative.Set2

            for i, country in enumerate(compare_countries):
                cdf = df[df['country'] == country].copy().sort_values('date')
                if cdf.empty:
                    continue

                if metric_choice == 'daily_vaccinations':
                    cdf_i  = cdf.set_index('date')
                    ts_c   = cdf_i['daily_vaccinations'].copy()
                    full_r = pd.date_range(ts_c.index.min(), ts_c.index.max(), freq='D')
                    ts_c   = ts_c.reindex(full_r).interpolate(method='linear').clip(lower=0)
                    ts_c   = ts_c.rolling(7, min_periods=1).mean()
                    x_vals = ts_c.index
                    y_vals = ts_c.values
                else:
                    x_vals = cdf['date']
                    y_vals = cdf[metric_choice]

                fig_cmp.add_trace(go.Scatter(
                    x=x_vals, y=y_vals,
                    mode='lines',
                    line=dict(color=colors_cmp[i % len(colors_cmp)], width=2.2),
                    name=country,
                    hovertemplate=(
                        f'<b>{country}</b><br>'
                        '%{x|%b %d %Y}<br>%{y:,.0f}<extra></extra>'
                    )
                ))

            metric_labels = {
                'daily_vaccinations':                  'Daily Vaccinations (7d MA)',
                'total_vaccinations':                  'Total Cumulative Doses',
                'people_fully_vaccinated_per_hundred': 'People Fully Vaccinated per 100'
            }

            fig_cmp.update_layout(
                template='plotly_white',
                height=520,
                xaxis_title='Date',
                yaxis_title=metric_labels[metric_choice],
                hovermode='x unified',
                legend=dict(
                    orientation='h',
                    yanchor='bottom', y=1.02,
                    xanchor='right',  x=1
                )
            )
            st.plotly_chart(fig_cmp, use_container_width=True)

            st.markdown("#### 📊 Summary Statistics")
            rows = []
            for country in compare_countries:
                cdf = df[df['country'] == country]
                if cdf.empty:
                    continue
                rows.append({
                    'Country':            country,
                    'Total Doses':        format_millions(cdf['total_vaccinations'].max()),
                    'Peak Daily':         format_millions(cdf['daily_vaccinations'].max()),
                    '% Fully Vaccinated': f"{cdf['people_fully_vaccinated_per_hundred'].max():.1f}%",
                    'Data Start':         str(cdf['date'].min().date()),
                    'Data End':           str(cdf['date'].max().date()),
                })
            if rows:
                st.dataframe(
                    pd.DataFrame(rows),
                    use_container_width=True,
                    hide_index=True
                )

    # ══════════════════════════════════════════════════════════
    # TAB 5 — DATA EXPLORER
    # ══════════════════════════════════════════════════════════
    with tab5:
        st.markdown("### 📋 Interactive Data Explorer")

        col_f1, col_f2, col_f3 = st.columns(3)

        with col_f1:
            filter_countries = st.multiselect(
                "Filter by country:",
                options=countries,
                default=[selected_country]
            )
        with col_f2:
            date_min  = df['date'].min().date()
            date_max  = df['date'].max().date()
            date_from = st.date_input(
                "From:", value=date_min,
                min_value=date_min, max_value=date_max
            )
        with col_f3:
            date_to = st.date_input(
                "To:", value=date_max,
                min_value=date_min, max_value=date_max
            )

        filtered = df.copy()
        if filter_countries:
            filtered = filtered[filtered['country'].isin(filter_countries)]
        filtered = filtered[
            (filtered['date'] >= pd.Timestamp(date_from)) &
            (filtered['date'] <= pd.Timestamp(date_to))
        ]

        display_cols = [c for c in [
            'country', 'date', 'total_vaccinations',
            'people_vaccinated', 'people_fully_vaccinated',
            'people_fully_vaccinated_per_hundred',
            'daily_vaccinations', 'vaccines'
        ] if c in filtered.columns]

        st.markdown(f"Showing **{len(filtered):,}** records")
        st.dataframe(
            filtered[display_cols].head(1000),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label="📥 Download Filtered Data as CSV",
            data=filtered[display_cols].to_csv(index=False),
            file_name="vaccination_data_filtered.csv",
            mime='text/csv'
        )

        st.markdown("---")
        st.markdown("#### 📊 Descriptive Statistics")
        num_cols = [c for c in [
            'total_vaccinations', 'people_fully_vaccinated',
            'daily_vaccinations', 'people_fully_vaccinated_per_hundred'
        ] if c in filtered.columns]

        if num_cols:
            st.dataframe(
                filtered[num_cols].describe().round(2),
                use_container_width=True
            )

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#888; font-size:0.85rem;'>"
    "COVID-19 Global Vaccination Analysis · "
    "Data: Kaggle — COVID-19 World Vaccination Progress · "
    "Built with Streamlit &amp; statsmodels"
    "</div>",
    unsafe_allow_html=True
)
