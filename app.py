import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from data_processing import (
    calculate_health_score,
    clean_inventario,
    clean_transacciones,
    clean_feedback,
    merge_datasets
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
    "Auditoría de datos, integración y análisis de riesgo para una operación *Tech + Logistics*."
)

# --------------------------------------------------
# Sidebar – Ingesta
# --------------------------------------------------
st.sidebar.title("Carga de Datos")

inv_file = st.sidebar.file_uploader("Inventario", type="csv")
tx_file  = st.sidebar.file_uploader("Transacciones", type="csv")
fb_file  = st.sidebar.file_uploader("Feedback Clientes", type="csv")

run_btn = st.sidebar.button("🧹 Ejecutar Limpieza y Análisis")

# --------------------------------------------------
# Ejecución del pipeline
# --------------------------------------------------
if run_btn:

    if not all([inv_file, tx_file, fb_file]):
        st.error("Debes cargar los tres archivos.")
        st.stop()

    # -------- Ingesta RAW --------
    df_inv_raw = pd.read_csv(inv_file)
    df_tx_raw  = pd.read_csv(tx_file)
    df_fb_raw  = pd.read_csv(fb_file)

    # -------- Health BEFORE --------
    st.session_state["health_inv_before"] = calculate_health_score(df_inv_raw, "Inventario")
    st.session_state["health_tx_before"]  = calculate_health_score(df_tx_raw, "Transacciones")
    st.session_state["health_fb_before"]  = calculate_health_score(df_fb_raw, "Feedback")

    # -------- Limpieza --------
    df_inv_clean, log_inv = clean_inventario(df_inv_raw)
    df_tx_clean,  log_tx  = clean_transacciones(df_tx_raw)
    df_fb_clean,  log_fb  = clean_feedback(df_fb_raw)

    # -------- Health AFTER --------
    st.session_state["health_inv_after"] = calculate_health_score(df_inv_clean, "Inventario")
    st.session_state["health_tx_after"]  = calculate_health_score(df_tx_clean, "Transacciones")
    st.session_state["health_fb_after"]  = calculate_health_score(df_fb_clean, "Feedback")

    # -------- Integración --------
    df_master, metrics = merge_datasets(
        df_inv_clean,
        df_tx_clean,
        df_fb_clean
    )

    # -------- Persistencia --------
    st.session_state["df_master"] = df_master
    st.session_state["logs"] = {
        "Inventario": log_inv,
        "Transacciones": log_tx,
        "Feedback": log_fb
    }
    st.session_state["metrics"] = metrics

# --------------------------------------------------
# Validación
# --------------------------------------------------
if "df_master" not in st.session_state:
    st.info("Carga los archivos y ejecuta la limpieza.")
    st.stop()

df = st.session_state["df_master"]

# --------------------------------------------------
# Tabs principales
# --------------------------------------------------
tab_audit, tab_ops, tab_client, tab_risk = st.tabs(
    ["🧪 Auditoría", "📊 Operaciones", "😊 Cliente", "⚠️ Riesgo"]
)

# --------------------------------------------------
# 🧪 TAB 1 – Auditoría
# --------------------------------------------------
with tab_audit:
    st.subheader("Health Score – Antes vs Después")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Inventario",
        st.session_state["health_inv_after"]["health_score"],
        st.session_state["health_inv_after"]["health_score"] -
        st.session_state["health_inv_before"]["health_score"]
    )

    col2.metric(
        "Transacciones",
        st.session_state["health_tx_after"]["health_score"],
        st.session_state["health_tx_after"]["health_score"] -
        st.session_state["health_tx_before"]["health_score"]
    )

    col3.metric(
        "Feedback",
        st.session_state["health_fb_after"]["health_score"],
        st.session_state["health_fb_after"]["health_score"] -
        st.session_state["health_fb_before"]["health_score"]
    )

    st.subheader("Decisiones de Limpieza")
    for k, logs in st.session_state["logs"].items():
        st.markdown(f"**{k}**")
        for l in logs:
            st.markdown(f"- {l}")

# --------------------------------------------------
# 📊 TAB 2 – Operaciones
# --------------------------------------------------
with tab_ops:
    st.subheader("Distribución del Margen de Utilidad")

    margen = df["Margen_USD"].dropna()
    p5, p95 = margen.quantile([0.05, 0.95])
    margen_vis = margen.clip(p5, p95)

    fig, ax = plt.subplots()
    ax.hist(margen_vis, bins=40)
    ax.axvline(0, linestyle="--")
    ax.set_xlabel("Margen (USD)")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    st.metric(
        "Ventas con SKU Fantasma",
        st.session_state["metrics"]["phantom_sales"]
    )

    st.metric(
        "Ingresos en Riesgo (USD)",
        round(st.session_state["metrics"]["phantom_revenue"], 2)
    )

# --------------------------------------------------
# 😊 TAB 3 – Cliente
# --------------------------------------------------
with tab_client:
    st.subheader("Tiempo de Entrega vs Satisfacción (NPS)")

    fig, ax = plt.subplots()
    ax.scatter(df["Tiempo_Entrega"], df["Satisfaccion_NPS"], alpha=0.3)
    ax.set_xlabel("Tiempo de Entrega (días)")
    ax.set_ylabel("NPS")
    st.pyplot(fig)

# --------------------------------------------------
# ⚠️ TAB 4 – Riesgo
# --------------------------------------------------
with tab_risk:
    st.subheader("Riesgo Operativo por Bodega")

    riesgo = (
        df
        .groupby("Bodega_Origen")["Ticket_Binary"]
        .mean()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots()
    riesgo.plot(kind="bar", ax=ax)
    ax.set_ylabel("Tasa de Tickets")
    st.pyplot(fig)
