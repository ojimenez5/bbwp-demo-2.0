%pip install streamlit
# bbwp_dashboard.py
import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import os

# ============================================
# 🔹 CONFIGURACIÓN INICIAL
# ============================================

st.set_page_config(page_title="BBWP Dashboard - Prueba", layout="wide")
st.title("📊 Prueba local: Cálculo de BBWP para 20 tickers")

# Lista de tickers de prueba (puedes cambiar o ampliar)
tickers = [
    "AAPL","MSFT","AMZN","META","GOOGL",
    "NVDA","TSLA","NFLX","AMD","INTC",
    "JPM","BAC","V","MA","XOM",
    "CVX","PEP","KO","DIS","WMT"
]

# ============================================
# 🔹 FUNCIÓN PARA CALCULAR BBWP
# ============================================

def calculate_bbwp(df, length=20):
    """
    Calcula el indicador BBWP (Bollinger Band Width Percentile)
    a partir de precios de cierre.
    """
    df["MA"] = df["Close"].rolling(window=length).mean()
    df["STD"] = df["Close"].rolling(window=length).std()
    df["Upper"] = df["MA"] + 2 * df["STD"]
    df["Lower"] = df["MA"] - 2 * df["STD"]
    df["BBW"] = (df["Upper"] - df["Lower"]) / df["MA"] * 100

    # Percentil móvil (BBWP)
    df["BBWP"] = df["BBW"].rolling(window=252).apply(
        lambda x: np.sum(x <= x.iloc[-1]) / len(x) * 100 if len(x.dropna()) > 0 else np.nan,
        raw=False
    )
    return df

# ============================================
# 🔹 DESCARGA Y PROCESAMIENTO
# ============================================

st.sidebar.header("⚙️ Configuración de descarga")
period = st.sidebar.selectbox("Periodo de datos", ["5y", "3y", "1y", "max"], index=0)
interval = st.sidebar.selectbox("Temporalidad", ["1d", "1wk"], index=0)
min_periods = st.sidebar.slider("Mínimo de periodos disponibles", 100, 500, 200)

if st.sidebar.button("▶️ Ejecutar análisis"):
    results = []

    progress = st.progress(0)
    for i, ticker in enumerate(tickers):
        try:
            df = yf.download(ticker, period=period, interval=interval, progress=False)
            if len(df) < min_periods:
                continue

            df = calculate_bbwp(df)

            last_vals = df["BBWP"].tail(6).values  # Últimos 6 periodos
            for j in range(6):
                if last_vals[j] < 15:
                    results.append({
                        "Ticker": ticker,
                        "Periodo": j + 1,
                        "BBWP": round(last_vals[j], 2)
                    })

        except Exception as e:
            st.warning(f"Error con {ticker}: {e}")

        progress.progress((i + 1) / len(tickers))

    # ============================================
    # 🔹 RESULTADOS
    # ============================================
    if results:
        df_results = pd.DataFrame(results)
        st.success(f"✅ Análisis completado: {len(df_results)} coincidencias encontradas.")
        st.dataframe(df_results)

