import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import datetime

# ===========================================
# 🔹 Configuración inicial
# ===========================================
st.set_page_config(page_title="BBWP Dashboard", layout="wide")
st.title("📊 BBWP Dashboard (Versión de Prueba con 20 Tickers)")
st.markdown("Calcula el indicador BBWP para 20 activos en temporalidad diaria y semanal.")

# ===========================================
# 🔹 Lista de tickers de prueba
# ===========================================
tickers = [
    "AGNC","AMAT","AAPL","AFRM","ABNB","ABBV","AAL","AMD","AC","BAC","AXP","AVGO","BA","C","BMY","AMZN","CAT","CLF","COST","CRM","CSCO","CVS","CVX","DAL","DIS","DVN","ETSY","F","FANG","FCX","FDX","FSLR","FUBO","BIMBO A","CHDRAUI B","BBAJIO O","AMX B","GAP B","ALPEK A","BABA N","ASUR B","BOLSA A","GE","HD","GCC","GME","GOOGL","GM","KO","INTC","JNJ","JPM","LCID","KIMBER A","LLY","ALFA A","LAB B","GFINBUR O","ACTINVR B","LVS","MARA","META","MCD","LUV","MA","MRK","MU","MSFT","MRNA","NFLX","NKE","NVAX","NVDA","ORCL","PARA","PG","PEP","PFE","PLTR","PYPL","PINS","QCOM","RCL","RIVN","RIOT","SBUX","SOFI","SPCE","T","TGT","TMO","TSLA","CEMEX CPO","TX","UAL","R A","KOF UBL","GRUMA B","GMEXICO B","WFC","WMT","VZ","XOM","ACWI","AAXJ","ZM","XYZ","BIL","BOTZ","DIA","EEM","EWZ","FAZ","FAS","GDX","IAU","GLD","INDA","KWEB","LIT","MCHI","IVV","QLD","QQQ","QCLN","PSQ","SHV","SOXL","SHY","SLV","SOXS","SPLG","SOXX","SPXS","SPXL","SQQQ","TECS","TECL","SPY","TAN","TLT","TQQQ","TNA","TZA","USO","VNQ","VEA","VT","VOO","VGT","VTI","VWO","VYM","XLE","XLK","XLV","MAYA","XLF","VOLAR A","TSM N","MELI N"
]

# ===========================================
# 🔹 Función para calcular BBWP
# ===========================================
def calcular_bbwp(df, periodo=20):
    if len(df) < periodo:
        return pd.Series([np.nan] * len(df), index=df.index)
    bb_range = df["Close"].rolling(periodo).max() - df["Close"].rolling(periodo).min()
    bb_width = (df["Close"] - df["Close"].rolling(periodo).min()) / bb_range * 100
    return bb_width

# ===========================================
# 🔹 Descargar datos desde Yahoo Finance
# ===========================================
@st.cache_data(show_spinner=True)
def descargar_datos(ticker, period="5y", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False)
        df.dropna(inplace=True)
        return df
    except Exception as e:
        st.warning(f"No se pudo descargar {ticker}: {e}")
        return None

# ===========================================
# 🔹 Análisis principal
# ===========================================
intervalo = st.radio("Selecciona intervalo de análisis:", ["1d (diario)", "1wk (semanal)"])
intervalo = "1wk" if "semanal" in intervalo else "1d"

st.info(f"Descargando datos en temporalidad {intervalo}...")

resultados = []

for ticker in tickers:
    df = descargar_datos(ticker, interval=intervalo)
    if df is None or df.empty:
        continue

    df["BBWP"] = calcular_bbwp(df)
    ultimo_valor = df["BBWP"].iloc[-1]

    # Revisar si los últimos 6 periodos tienen BBWP < 15
    ultimos = df["BBWP"].tail(6)
    condiciones = (ultimos < 15).sum()

    resultados.append({
        "Ticker": ticker,
        "Último BBWP": round(ultimo_valor, 2),
        "Periodos <15 (últimos 6)": int(condiciones)
    })

# ===========================================
# 🔹 Mostrar resultados
# ===========================================
df_resultados = pd.DataFrame(resultados).sort_values("Último BBWP")
st.dataframe(df_resultados, use_container_width=True)

# ===========================================
# 🔹 Descargar Excel
# ===========================================
excel_name = f"bbwp_resultados_{intervalo}.xlsx"
df_resultados.to_excel(excel_name, index=False)

with open(excel_name, "rb") as f:
    st.download_button(
        label="📥 Descargar resultados en Excel",
        data=f,
        file_name=excel_name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

st.success("✅ Análisis completado correctamente.")
