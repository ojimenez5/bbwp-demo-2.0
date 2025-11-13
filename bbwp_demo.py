import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf

# ===========================================
# 🔹 Configuración inicial
# ===========================================
st.set_page_config(page_title="BBWP Dashboard - 171 Tickers", layout="wide")
st.title("📊 BBWP Dashboard (171 Tickers)")
st.markdown("Calcula el indicador **BBWP** para los 171 activos disponibles del Reto Actinver en temporalidad diaria o semanal.")

# ===========================================
# 🔹 Lista de tickers (171)
# ===========================================
tickers = [
    "AGNC","AMAT","AAPL","AFRM","ABNB","ABBV","AAL","AMD","AC","BAC","AXP","AVGO","BA","BABA N","BBAJIO O",
    "BIMBO A","BK","BMY","BOLSA A","C","CAT","CEMEX CPO","CHDRAUI B","CLF","COIN","COST","CRM","CSCO","CVS","CVX","DAL",
    "DIS","DVN","ETSY","F","FANG","FCX","FDX","FSLR","FUBO","GAP B","GCC","GE","GFINBUR O","GFNORTE O","GM",
    "GME","GMEXICO B","GOOGL","GRUMA B","HD","INTC","JNJ","JPM","KIMBER A","KO","KOF UBL","LAB B","LCID","LLY",
    "LUV","LVS","MA","MARA","MCD","MELI N","META","MRK","MRNA","MSFT","MU","NCLH N","NFLX","NKE","NU N","NVAX",
    "NVDA","OMA B","ORCL","PARA","PDD","PEP","PFE","PG","PINS","PLTR","PPTA","PYPL","QCOM","R A","RCL","RIOT","RIVN","SBUX",
    "SHOP N","SOFI","SPCE","T","TGT","TMO","TSLA","TSM N","TX","UAL","UBER","UNH","UPST","V","VOLAR A","VZ","WFC",
    "WMT","XOM","XYZ","ZM","AAXJ","ACWI","BIL","BOTZ","DIA","EEM","EWZ","FAS","FAZ","GDX","GLD","IAU","ICLN",
    "INDA","IVV","KWEB","LIT","MCHI","PSQ","QCLN","QLD","QQQ","SHV","SHY","SLV","SOXL","SOXS","SOXX","SPLG",
    "SPXL","SPXS","SPY","SQQQ","TAN","TECL","TECS","TLT","TNA","TQQQ","TZA","USO","VEA","VGT","VNQ","VOO","VT",
    "VTI","VWO","VYM","XLE","XLF","XLK","XLV","MAYA"
]

# ===========================================
# 🔹 Función para calcular BBWP
# ===========================================
def calcular_bbwp(df, periodo=20):
    if len(df) < periodo:
        return pd.Series([np.nan] * len(df), index=df.index)
    rango = df["Close"].rolling(periodo).max() - df["Close"].rolling(periodo).min()
    ancho = (df["Close"] - df["Close"].rolling(periodo).min()) / rango * 100
    return ancho.reindex(df.index)

# ===========================================
# 🔹 Descargar datos desde Yahoo Finance
# ===========================================
@st.cache_data(show_spinner=False)
def descargar_datos(ticker, period="5y", interval="1d"):
    try:
        df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=True)
        if df is not None and not df.empty:
            df.dropna(inplace=True)
            return df
        else:
            return None
    except Exception:
        return None

# ===========================================
# 🔹 Selector de intervalo
# ===========================================
intervalo = st.radio("Selecciona intervalo de análisis:", ["1d (diario)", "1wk (semanal)"])
intervalo = "1wk" if "semanal" in intervalo else "1d"

st.info(f"⏳ Descargando datos y calculando BBWP ({intervalo}) para {len(tickers)} tickers...")

# ===========================================
# 🔹 Procesamiento principal
# ===========================================
resultados = []
total = len(tickers)
barra = st.progress(0)
exitosos = 0
fallidos = 0

for i, ticker in enumerate(tickers):
    df = descargar_datos(ticker, interval=intervalo)
    if df is None or df.empty:
        fallidos += 1
        continue

    try:
        df["BBWP"] = calcular_bbwp(df)
        if "BBWP" not in df or df["BBWP"].isna().all():
            continue

        ultimos6 = df["BBWP"].tail(6)
        bbwp_ultimo = df["BBWP"].iloc[-1]
        conteo_bajo = (ultimos6 < 15).sum()

        resultados.append({
            "Ticker": ticker,
            "Último BBWP": round(bbwp_ultimo, 2),
            "Periodos <15 (últimos 6)": int(conteo_bajo)
        })
        exitosos += 1

    except Exception:
        fallidos += 1
        continue

    barra.progress((i + 1) / total)

# ===========================================
# 🔹 Resultados y descarga
# ===========================================
if resultados:
    df_resultados = pd.DataFrame(resultados).sort_values("Último BBWP")
    st.dataframe(df_resultados, use_container_width=True)

    excel_name = f"bbwp_resultados_{intervalo}_171.xlsx"
    df_resultados.to_excel(excel_name, index=False)

    with open(excel_name, "rb") as f:
        st.download_button(
            label="📥 Descargar resultados en Excel",
            data=f,
            file_name=excel_name,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    st.success(f"✅ Cálculo completado. {exitosos} tickers exitosos, {fallidos} fallidos.")
else:
    st.error("⚠️ No se pudo obtener información de ningún ticker.")

