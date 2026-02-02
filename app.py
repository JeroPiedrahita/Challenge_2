
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unicodedata
import plotly.express as px
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

st.sidebar.header("🎛️ Filtros")

# Filtros básicos
bodegas = st.sidebar.multiselect(
    "Bodega de Origen",
    options=sorted(df_master["Bodega_Origen"].dropna().unique()),
    default=sorted(df_master["Bodega_Origen"].dropna().unique())
)

ciudades = st.sidebar.multiselect(
    "Ciudad Destino",
    options=sorted(df_master["Ciudad_Destino_Limpia"].dropna().unique()),
    default=sorted(df_master["Ciudad_Destino_Limpia"].dropna().unique())
)

canales = st.sidebar.multiselect(
    "Canal de Venta",
    options=sorted(df_master["Canal_Venta"].dropna().unique()),
    default=sorted(df_master["Canal_Venta"].dropna().unique())
)

# Aplicar filtros
df_f = df_master[
    (df_master["Bodega_Origen"].isin(bodegas)) &
    (df_master["Ciudad_Destino_Limpia"].isin(ciudades)) &
    (df_master["Canal_Venta"].isin(canales))
]

# --------------------------------------------------
# KPIs Ejecutivos
# --------------------------------------------------
st.subheader("📊 KPIs Operacionales")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ingresos Totales (USD)", f"${df_f['Ingreso'].sum():,.0f}")
col2.metric("Margen Total (USD)", f"${df_f['Margen_Utilidad'].sum():,.0f}")

margen_pct = (df_f["Margen_Utilidad"].sum() / df_f["Ingreso"].sum()) * 100
col3.metric("Margen Total (%)", f"{margen_pct:.1f}%")

col4.metric(
    "Ventas con SKU Fantasma (%)",
    f"{df_f['sku_fantasma'].mean() * 100:.1f}%"
)

# --------------------------------------------------
# Análisis interactivo de correlaciones
# --------------------------------------------------
st.subheader("🔍 Relación entre Variables Operativas y de Negocio")

st.markdown(
    """
    Explora cómo las variables logísticas y comerciales se relacionan entre sí.
    Cambia los ejes para descubrir patrones ocultos y cuellos de botella.
    """
)

variables_numericas = {
    "Tiempo de Entrega": "Tiempo_Entrega_Limpio",
    "Brecha de Entrega": "Brecha_Entrega",
    "Margen de Utilidad": "Margen_Utilidad",
    "Ingreso por Venta": "Ingreso",
    "Satisfacción (NPS)": "Satisfaccion_NPS",
    "Rating Logística": "Rating_Logistica",
    "Rating Producto": "Rating_Producto"
}

colx, coly, colc = st.columns(3)

x_var_label = colx.selectbox("Eje X", variables_numericas.keys(), index=0)
y_var_label = coly.selectbox("Eje Y", variables_numericas.keys(), index=4)

color_var = colc.selectbox(
    "Color por",
    ["Canal_Venta", "Bodega_Origen", "Estado_Envio"],
    index=0
)

x_var = variables_numericas[x_var_label]
y_var = variables_numericas[y_var_label]

fig = px.scatter(
    df_f,
    x=x_var,
    y=y_var,
    color=color_var,
    hover_data=[
        "SKU_ID",
        "Ciudad_Destino_Limpia",
        "Canal_Venta"
    ],
    opacity=0.6,
    trendline="ols",
    title=f"{y_var_label} vs {x_var_label}"
)

fig.update_layout(
    template="plotly_white",
    height=500,
    legend_title_text=color_var.replace("_", " ")
)

st.plotly_chart(fig, use_container_width=True)


st.markdown(
    f"""
    **📌 Interpretación rápida:**

    La correlación entre **{x_var_label}** y **{y_var_label}** es de  
    **{corr:.2f}**, lo que sugiere una relación 
    {"fuerte" if abs(corr) > 0.6 else "moderada" if abs(corr) > 0.3 else "débil"}.

    Esto puede indicar oportunidades de optimización operativa o riesgos
    que impactan directamente la experiencia del cliente.
    """
)

st.subheader("💡 ¿Dónde se gana y dónde se pierde dinero?")

fig = px.box(
    df_f,
    x="Bodega_Origen",
    y="Margen_Utilidad",
    color="Bodega_Origen",
    title="Distribución de Margen por Bodega"
)

fig.update_layout(
    template="plotly_white",
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# Rentabilidad
# --------------------------------------------------
st.subheader("💰 Rentabilidad por Bodega")

margen_bodega = (
    df_f.groupby("Bodega_Origen")["Margen_Utilidad"]
    .mean()
    .sort_values()
)

fig, ax = plt.subplots()
margen_bodega.plot(kind="barh", ax=ax)
ax.set_xlabel("Margen promedio (USD)")
st.pyplot(fig)

# --------------------------------------------------
# Logística vs Satisfacción
# --------------------------------------------------
st.subheader("🚚 Logística y Satisfacción")

fig, ax = plt.subplots()
ax.scatter(
    df_f["Tiempo_Entrega_Limpio"],
    df_f["Satisfaccion_NPS"],
    alpha=0.3
)
ax.set_xlabel("Tiempo de Entrega (días)")
ax.set_ylabel("NPS")
st.pyplot(fig)

# --------------------------------------------------
# Riesgo Operativo
# --------------------------------------------------
st.subheader("⚠️ Riesgo Operativo por Bodega")

riesgo = (
    df_f
    .assign(ticket_bin=df_f["Ticket_Soporte_Abierto"] == "Sí")
    .groupby("Bodega_Origen")["ticket_bin"]
    .mean()
    .sort_values(ascending=False)
)

fig, ax = plt.subplots()
riesgo.plot(kind="bar", ax=ax)
ax.set_ylabel("Tasa de Tickets")
st.pyplot(fig)



