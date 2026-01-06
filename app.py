import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="Penukar Mata Wang Harian", page_icon="💱", layout="centered")

# --- 2. SIDEBAR (TEMA & INFO) ---
with st.sidebar:
    st.header("⚙️ Tetapan")
    tema = st.radio("Pilih Tema:", ["🌙 Mode Gelap (Dark)", "☀️ Mode Cerah (Light)"])
    st.divider()
    st.info("Data diambil dari Yahoo Finance berdasarkan harga penutup pasaran (Market Close).")
    st.caption("Update: Sekali sehari (Daily Close).")

# --- CSS TEMA ---
if tema == "☀️ Mode Cerah (Light)":
    st.markdown("""
        <style>
            .stApp { background-color: #ffffff; color: #000000; }
            .stNumberInput input { color: #000000 !important; background-color: #f0f2f6 !important; }
            .stMarkdown, .stText, p, label, .stMetricLabel { color: #000000 !important; }
            div[data-testid="stMetricValue"] { color: #000000 !important; }
        </style>
    """, unsafe_allow_html=True)

# --- 3. FUNGSI TARIK DATA (YFINANCE - DIPERBAIKI) ---
@st.cache_data(ttl=3600)
def get_exchange_rate(pair_code, period="1mo"):
    # Format Yahoo: USDMYR=X
    ticker_symbol = f"{pair_code}=X"
    
    try:
        # Guna yf.Ticker().history() -> Lebih stabil dari yf.download()
        ticker_data = yf.Ticker(ticker_symbol)
        data = ticker_data.history(period=period)
        
        if not data.empty and len(data) > 1:
            latest_rate = data['Close'].iloc[-1] # Harga tutup terkini
            prev_rate = data['Close'].iloc[-2]   # Harga tutup semalam
            history = data['Close']              # Data untuk graf
            
            # Format tarikh
            last_date = data.index[-1]
            date_str = last_date.strftime('%d %b %Y')
            
            return latest_rate, prev_rate, history, date_str
        else:
            return None, None, None, None
            
    except Exception as e:
        return None, None, None, None

# --- 4. UI UTAMA ---
st.title("💱 Penukar Mata Wang Live")
st.caption("Lihat trend mata wang harian berbanding Ringgit Malaysia (MYR).")

st.subheader("1. Pilih Mata Wang")

col1, col2 = st.columns([1, 2])

# Input Amount
with col1:
    amount = st.number_input("Jumlah Asing", value=1.00, min_value=0.01, format="%.2f")

# Pilihan Mata Wang (Key Pair)
currency_options = {
    "🇺🇸 USD - Dolar Amerika": "USDMYR",
    "🇸🇬 SGD - Dolar Singapura": "SGDMYR",
    "🇬🇧 GBP - Pound British": "GBPMYR",
    "🇪🇺 EUR - Euro Eropah": "EURMYR",
    "🇦🇺 AUD - Dolar Australia": "AUDMYR",
    "🇯🇵 JPY - Yen Jepun": "JPYMYR",
    "🇹🇭 THB - Baht Thailand": "THBMYR",
    "🇮🇩 IDR - Rupiah Indonesia": "IDRMYR",
    "🇸🇦 SAR - Riyal Saudi": "SARMYR",
    "🇨🇳 CNY - Yuan China": "CNYMYR"
}

with col2:
    selected_label = st.selectbox("Tukar Kepada Ringgit (MYR):", list(currency_options.keys()))
    pair_code = currency_options[selected_label]

st.divider()

# --- 5. PAPARAN KEPUTUSAN ---
if st.button("🔄 Semak Kadar Terkini", type="primary"):
    
    with st.spinner(f"Sedang menyemak kadar {pair_code}..."):
        rate, prev_rate, history, update_date = get_exchange_rate(pair_code)
    
    if rate:
        # Kiraan
        converted_value = amount * rate
        perubahan = rate - prev_rate
        perubahan_pct = (perubahan / prev_rate) * 100
        
        st.subheader("2. Keputusan Tukaran")
        
        # Grid Layout Cantik
        m1, m2, m3 = st.columns(3)
        
        # 1. Nilai Hasil
        m1.metric(label=f"Nilai dalam MYR", 
                  value=f"RM {converted_value:,.2f}", 
                  help="Jumlah duit asing x Rate Terkini")
        
        # 2. Rate Satu Unit
        m2.metric(label=f"1 {pair_code[:3]} = ", 
                  value=f"RM {rate:.4f}", 
                  delta=f"{perubahan_pct:.2f}% (Sehari)",
                  help="Perubahan berbanding harga tutup semalam")
            
        # 3. Tarikh Data
        m3.write(f"**Tarikh Data:**\n{update_date}")
        m3.caption("*Ikut waktu tutup New York/Global*")
        
        # --- 6. GRAF TREND ---
        st.divider()
        st.subheader(f"📉 Trend 30 Hari ({pair_code[:3]} vs MYR)")
        
        # Bersihkan data graf
        chart_data = pd.DataFrame(history)
        chart_data.columns = ["Kadar Tukaran"]
        
        # Papar Graf
        st.line_chart(chart_data, color="#00FF00")
        
        with st.expander("Lihat Data Mentah (Jadual)"):
            st.dataframe(chart_data.sort_index(ascending=False))
            
    else:
        st.error(f"Maaf, data {pair_code} tidak dapat diambil buat masa ini. Sila cuba mata wang lain atau 'Refresh' page.")
        st.caption("Tip: Kadang-kala Yahoo Finance menghadkan akses jika terlalu kerap refresh.")
