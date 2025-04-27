import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import urllib.error
from datetime import datetime

st.set_page_config(page_title="Global Earthquake Correlation & Prediction App", layout="wide")
st.title("Global Earthquake Correlation & Prediction")

# Veri çekme fonksiyonu
def fetch_earthquake_data(min_magnitude=4.0):
    try:
        # USGS earthquake feed URL
        if min_magnitude >= 4.5:
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_month.csv"
        else:
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.csv"
        df = pd.read_csv(url)
        return df
    except urllib.error.HTTPError as e:
        st.error(f"HTTP Error occurred: {e.code} - {e.reason}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return pd.DataFrame()

# Verileri filtreleme
def filter_by_region(df, region_keywords):
    mask = df['place'].str.contains('|'.join(region_keywords), case=False, na=False)
    return df[mask]

# Korelasyon örneği
def calculate_correlation(df, region1_keywords, region2_keywords):
    df_region1 = filter_by_region(df, region1_keywords)
    df_region2 = filter_by_region(df, region2_keywords)

    if df_region1.empty or df_region2.empty:
        return None

    data = {
        'region1_counts': [len(df_region1)],
        'region2_counts': [len(df_region2)]
    }
    corr_df = pd.DataFrame(data)
    correlation = corr_df.corr().iloc[0, 1]
    return correlation

# Ana uygulama
st.sidebar.header("Filtre Ayarları")
min_magnitude = st.sidebar.slider("Minimum Magnitude", 4.0, 10.0, 4.0)

region1 = st.sidebar.text_input("Bölge 1 Anahtar Kelimeler (virgül ile ayırın):", "Myanmar")
region2 = st.sidebar.text_input("Bölge 2 Anahtar Kelimeler (virgül ile ayırın):", "Istanbul, Marmara")

if st.sidebar.button("Verileri Getir ve Analiz Et"):
    with st.spinner('Veriler getiriliyor...'):
        df = fetch_earthquake_data(min_magnitude)
        if not df.empty:
            st.success('Veriler getirildi!')

            st.subheader("Son Deprem Verileri")
            st.dataframe(df[['time', 'place', 'mag']].head(100))

            st.subheader("Deprem Magnitude Dağılımı")
            fig, ax = plt.subplots()
            df['mag'].hist(bins=30, ax=ax)
            plt.title('Magnitude Distribution')
            plt.xlabel('Magnitude')
            plt.ylabel('Frequency')
            plt.grid(True)
            fig.savefig('magnitude_distribution.png')  # Grafik kaydetme
            st.pyplot(fig)

            st.subheader("Korelasyon Analizi")
            region1_keywords = [k.strip() for k in region1.split(',')]
            region2_keywords = [k.strip() for k in region2.split(',')]

            correlation = calculate_correlation(df, region1_keywords, region2_keywords)

            if correlation is not None:
                st.success(f"Bölge 1 ile Bölge 2 arasında korelasyon: {correlation:.2f}")
            else:
                st.error("Korelasyon hesaplanamadı. Veriler yetersiz.")
        else:
            st.error("Veriler çekilemedi, lütfen sonra tekrar deneyin.")
