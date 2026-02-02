
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unicodedata
from data_processing import (
    clean_inventario,
    clean_transacciones,
    clean_feedback
)


# --------------------------------------------------
# Configuración general
# --------------------------------------------------
st.set_page_config(
    page_title="EDA Operacional – TechLog",
    layout="wide"
)

st.title("📦 EDA Operacional – TechLog")
st.markdown(
    "Auditoría de datos, integración y análisis de riesgo para una operación **Tech + Logistics**."
)

# --------------------------------------------------
# Funciones auxiliares
# --------------------------------------------------
def norm(x):
    if pd.isna(x):
        return x
    x = str(x).strip().lower()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

def nps_grupo(x):
    if pd.isna(x): return np.nan
    if x >= 9: return "Promotor"
    if x >= 7: return "Pasivo"
    return "Detractor"

def health_report(df_raw, df_clean):
    pct_nulos = df_clean.isna().mean() * 100
    duplicados = len(df_raw) - len(df_raw.drop_duplicates())

    num = df_clean.select_dtypes(include=np.number)
    outliers = ((num - num.mean()).abs() > 3 * num.std()).sum().sum()

    health = max(
        0,
        100 - (
            pct_nulos.mean() * 0.4 +
            (duplicados / len(df_raw)) * 100 * 0.2 +
            (outliers / max(1, num.size)) * 100 * 0.4
        )
    )

    return {
        "health_score": round(health, 1),
        "pct_nulos": pct_nulos,
        "duplicados": duplicados,
        "outliers": int(outliers)
    }

# --------------------------------------------------
# Sidebar – Ingesta
# --------------------------------------------------
st.sidebar.title("Carga de Datos")

inv_file = st.sidebar.file_uploader("Inventario", type="csv")
tx_file  = st.sidebar.file_uploader("Transacciones", type="csv")
fb_file  = st.sidebar.file_uploader("Feedback Clientes", type="csv")

if st.sidebar.button("🧹 Ejecutar Limpieza"):

    if not all([inv_file, tx_file, fb_file]):
        st.error("Debes cargar los tres archivos.")
        st.stop()

    # ---------------- Ingesta ----------------
    df_inv_raw = pd.read_csv(inv_file, dtype=str)
    df_tx_raw  = pd.read_csv(tx_file, dtype=str)
    df_fb_raw  = pd.read_csv(fb_file, dtype=str)

    # ---------------- Limpieza ----------------
    df_inv = clean_inventario(df_inv_raw)
    df_tx  = clean_transacciones(df_tx_raw)
    df_fb  = clean_feedback(df_fb_raw)

    # ---------------- Auditoría ----------------
    st.session_state["rep_inv"] = health_report(df_inv_raw, df_inv)
    st.session_state["rep_tx"]  = health_report(df_tx_raw, df_tx)
    st.session_state["rep_fb"]  = health_report(df_fb_raw, df_fb)

    # ---------------- Guardar ----------------
    st.session_state["df_inv"] = df_inv
    st.session_state["df_tx"]  = df_tx
    st.session_state["df_fb"]  = df_fb


# --------------------------------------------------
# Validación
# --------------------------------------------------
if "df_inv" not in st.session_state:
    st.info("Carga los archivos y ejecuta la limpieza.")
    st.stop()

df_inv = st.session_state["df_inv"]
df_tx  = st.session_state["df_tx"]
df_fb  = st.session_state["df_fb"]

# --------------------------------------------------
# Auditoría visual
# --------------------------------------------------
st.subheader("Auditoría de Calidad")

col1, col2, col3 = st.columns(3)
col1.metric("Health Inventario", st.session_state["rep_inv"]["health_score"])
col2.metric("Health Transacciones", st.session_state["rep_tx"]["health_score"])
col3.metric("Health Feedback", st.session_state["rep_fb"]["health_score"])

# --------------------------------------------------
# Integración
# --------------------------------------------------
df_master = (
    df_tx
    .merge(df_inv, on="SKU_ID", how="left", indicator=True)
    .merge(df_fb, on="Transaccion_ID", how="left")
)

df_master["sku_fantasma"] = df_master["_merge"] == "left_only"
df_master["Ingreso"] = df_master["Cantidad_Vendida"] * df_master["Precio_Venta_Final"]
df_master["Costo_Total"] = df_master["Cantidad_Vendida"] * df_master["Costo_Unitario_Limpio"] + df_master["Costo_Envio"]
df_master["Margen_Utilidad"] = df_master["Ingreso"] - df_master["Costo_Total"]
df_master["Brecha_Entrega"] = df_master["Tiempo_Entrega_Limpio"] - df_master["Lead_Time_Limpio"]

# --------------------------------------------------
# Storytelling visual
# --------------------------------------------------
st.subheader("Rentabilidad Operativa")

# 🔹 Mejora visual del margen (sin alterar datos)
margen = df_master["Margen_Utilidad"].dropna()
p5, p95 = margen.quantile([0.05, 0.95])
margen_vis = margen.clip(p5, p95)

fig, ax = plt.subplots()
ax.hist(margen_vis, bins=40)
ax.axvline(0, linestyle="--")
ax.set_xlabel("Margen de Utilidad (USD)")
ax.set_ylabel("Frecuencia")
ax.set_title("Distribución del Margen de Utilidad (recorte visual 5%–95%)")
st.pyplot(fig)

st.subheader("Impacto Logístico en Satisfacción")

fig, ax = plt.subplots()
ax.scatter(df_master["Tiempo_Entrega_Limpio"], df_master["Satisfaccion_NPS"], alpha=0.3)
ax.set_xlabel("Tiempo de Entrega (días)")
ax.set_ylabel("NPS")
st.pyplot(fig)

st.subheader("Riesgo Operativo por Bodega")

riesgo = (
    df_master
    .assign(ticket_bin=df_master["Ticket_Soporte_Abierto"] == "Sí")
    .groupby("Bodega_Origen")["ticket_bin"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots()
riesgo.plot(kind="bar", ax=ax)
ax.set_ylabel("Tasa de Tickets")
st.pyplot(fig)
