import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import calendar

# Mengatur gaya visual seaborn
sns.set(style='darkgrid')

# --- HELPER FUNCTIONS ---
def create_daily_trend_df(df, pollutant):
    daily_df = df.resample(rule='D', on='datetime').agg({
        pollutant: 'mean',
        'station': 'first'
    }).reset_index()
    return daily_df

def create_monthly_df(df, pollutant):
    monthly_df = df.groupby(by="month").agg({
        pollutant: 'mean'
    }).reset_index()
    monthly_df['month_name'] = monthly_df['month'].apply(lambda x: calendar.month_name[x])
    return monthly_df

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        # Pastikan file csv ada di folder yang sama
        df = pd.read_csv("all_stations_df.csv")
        # Gabungkan kolom waktu menjadi datetime
        df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# Konfigurasi Halaman
st.set_page_config(page_title="Air Quality Dashboard", page_icon="⛅", layout="wide")

all_df = load_data()

if all_df.empty:
    st.error("File 'all_stations_df.csv' tidak ditemukan. Pastikan file berada di direktori yang sama.")
    st.stop()

# Urutkan data berdasarkan waktu
all_df.sort_values(by="datetime", inplace=True)

# --- SIDEBAR & FILTER (Dikembalikan seperti kode awal) ---
st.sidebar.header("Filter Dashboard")
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3222/3222806.png", width=50)

# 1. Filter Stasiun
station_list = sorted(all_df['station'].unique().tolist())
selected_stations = st.sidebar.multiselect("Pilih Stasiun:", station_list, default=station_list)


# 3. Filter Lanjutan (Bulan/Tahun) - Fitur dari kode awal
with st.sidebar.expander("Filter Lanjutan (Bulan/Tahun)"):
    # Filter Tahun
    years_list = sorted(all_df['year'].unique().tolist())
    selected_year = st.selectbox("Pilih Tahun:", options=['Semua'] + years_list)
    
    # Filter Bulan
    selected_months = st.multiselect(
        "Pilih Bulan:",
        options=range(1, 13),
        default=range(1, 13),
        format_func=lambda x: calendar.month_name[x]
    )

# 4. Filter Polutan
pollutant_options = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']
selected_pollutant = st.sidebar.radio("Pilih Parameter Polutan:", pollutant_options)

# --- LOGIKA FILTERING ---
# Filter 1: Stasiun
main_df = all_df[all_df['station'].isin(selected_stations)]

# Filter 3: Tahun (Jika tidak pilih 'Semua')
if selected_year != 'Semua':
    main_df = main_df[main_df['year'] == selected_year]

# Filter 4: Bulan
if selected_months:
    main_df = main_df[main_df['month'].isin(selected_months)]
else:
    st.warning("Mohon pilih setidaknya satu bulan.")
    st.stop()

# Cek Data Kosong
if main_df.empty:
    st.warning("Data tidak ditemukan untuk kombinasi filter ini.")
    st.stop()

# --- SIAPKAN DATA VISUALISASI ---
daily_trend_df = create_daily_trend_df(main_df, selected_pollutant)
monthly_df = create_monthly_df(main_df, selected_pollutant)

# --- DASHBOARD LAYOUT ---
st.title("📊 Dashboard Kualitas Udara: Beijing")
st.markdown(f"Analisis parameter **{selected_pollutant}**.")

# 1. KPI
col1, col2, col3 = st.columns(3)
with col1:
    avg_val = main_df[selected_pollutant].mean()
    st.metric(f"Rata-rata {selected_pollutant}", value=f"{avg_val:.2f}")
with col2:
    max_val = main_df[selected_pollutant].max()
    st.metric(f"Maksimum {selected_pollutant}", value=f"{max_val:.2f}")
with col3:
    rain_val = main_df['RAIN'].mean()
    st.metric("Curah Hujan (Rata-rata)", value=f"{rain_val:.2f} mm")

st.markdown("---")

# 2. GRAFIK TREN (Line Chart)
st.subheader(f"Tren Harian {selected_pollutant}")

fig_trend, ax_trend = plt.subplots(figsize=(16, 6))
sns.lineplot(
    data=daily_trend_df,
    x="datetime",
    y=selected_pollutant,
    hue="station",
    palette="bright",
    linewidth=2,
    ax=ax_trend
)
ax_trend.set_title(f"Pergerakan Harian {selected_pollutant}", fontsize=15)
ax_trend.set_xlabel("Tanggal")
ax_trend.set_ylabel(f"Konsentrasi {selected_pollutant}")
ax_trend.legend(title="Stasiun")
st.pyplot(fig_trend)

# 3. GRAFIK MUSIMAN (Bar Chart)
st.subheader("Analisis Pola Bulanan")

fig_month, ax_month = plt.subplots(figsize=(10, 6))
sns.barplot(
    x="month_name",
    y=selected_pollutant,
    data=monthly_df,
    palette="Reds",
    ax=ax_month,
    order=[calendar.month_name[i] for i in range(1, 13) if i in monthly_df['month'].unique()]
)
ax_month.set_title(f"Rata-rata {selected_pollutant} per Bulan", fontsize=15)
ax_month.set_xlabel("Bulan")
ax_month.set_xticklabels(ax_month.get_xticklabels(), rotation=45)
st.pyplot(fig_month)

# 4. KORELASI & SCATTER
st.markdown("---")
st.subheader("Analisis Korelasi & Cuaca")
col_sc1, col_sc2 = st.columns(2)

with col_sc1:
    st.markdown("**Hubungan Hujan vs Polusi**")
    fig_sc, ax_sc = plt.subplots(figsize=(8, 6))
    sns.scatterplot(
        x="RAIN",
        y=selected_pollutant,
        data=main_df,
        hue="station",
        alpha=0.6,
        ax=ax_sc
    )
    ax_sc.set_title("Efek Hujan (Washout Effect)")
    st.pyplot(fig_sc)

with col_sc2:
    st.markdown("**Heatmap Korelasi**")
    corr_cols = [selected_pollutant, 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    available_cols = [c for c in corr_cols if c in main_df.columns]
    
    if len(available_cols) > 1:
        corr_matrix = main_df[available_cols].corr()
        fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            corr_matrix, 
            annot=True, 
            fmt=".2f", 
            cmap="coolwarm", 
            ax=ax_corr
        )
        st.pyplot(fig_corr)

st.caption("Dashboard dibuat dengan Streamlit & Matplotlib")