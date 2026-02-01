import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# --------------------------------------------------
# Configuración general
# --------------------------------------------------
st.set_page_config(
    page_title="EDA Operacional",
    layout="wide"
)

# --------------------------------------------------
# Carga de datos (cacheada)
# --------------------------------------------------
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df_inv = load_data("inventario_limpio.csv")
df_tx  = load_data("transacciones_limpio.csv")
df_fb  = load_data("feedback_limpio.csv")

# --------------------------------------------------
# Sidebar – Navegación
# --------------------------------------------------
st.sidebar.title("EDA – Navegación")

seccion = st.sidebar.radio(
    "Selecciona el módulo:",
    [
        "Inventario",
        "Transacciones & Logística",
        "Feedback Clientes"
    ]
)

# ==================================================
# 📦 EDA INVENTARIO
# ==================================================
if seccion == "Inventario":

    st.title("📦 EDA – Inventario")
    st.markdown(
        "Análisis exploratorio del estado del inventario y riesgos operativos."
    )

    # KPIs
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "SKUs Totales",
        df_inv["SKU_ID"].nunique()
    )

    col2.metric(
        "Stock Negativo",
        int(df_inv["stock_negativo"].sum())
    )

    col3.metric(
        "Riesgo de Quiebre",
        int(df_inv["riesgo_quiebre"].sum())
    )

    # Distribución de costos
    st.subheader("Distribución del Costo Unitario")

    fig, ax = plt.subplots()
    df_inv["Costo_Unitario_Limpio"].dropna().plot(
        kind="hist",
        bins=30,
        ax=ax
    )
    ax.set_xlabel("Costo Unitario (USD)")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    # Stock vs Punto de Reorden
    st.subheader("Stock vs Punto de Reorden")

    fig, ax = plt.subplots()
    ax.scatter(
        df_inv["Punto_Reorden_Limpio"],
        df_inv["Stock_Analitico"],
        alpha=0.6
    )
    ax.set_xlabel("Punto de Reorden")
    ax.set_ylabel("Stock Analítico")
    st.pyplot(fig)

# ==================================================
# 🚚 EDA TRANSACCIONES & LOGÍSTICA
# ==================================================
if seccion == "Transacciones & Logística":

    st.title("🚚 EDA – Transacciones y Logística")
    st.markdown(
        "Evaluación de ingresos, tiempos de entrega e integridad referencial."
    )

    # Filtro por ciudad
    ciudad = st.sidebar.selectbox(
        "Ciudad destino",
        ["Todas"] + sorted(
            df_tx["Ciudad_Destino_Limpia"]
            .dropna()
            .unique()
            .tolist()
        )
    )

    df_tx_f = df_tx.copy()
    if ciudad != "Todas":
        df_tx_f = df_tx_f[
            df_tx_f["Ciudad_Destino_Limpia"] == ciudad
        ]

    # KPIs
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Ingresos Totales",
        f"${df_tx_f['Ingreso_Total'].sum():,.0f}"
    )

    col2.metric(
        "Ventas sin Catálogo",
        int(df_tx_f["producto_sin_catalogo"].sum())
    )

    col3.metric(
        "Tiempo Entrega Mediano (días)",
        int(df_tx_f["Tiempo_Entrega_Limpio"].median())
    )

    # Distribución tiempos de entrega
    st.subheader("Distribución del Tiempo de Entrega")

    fig, ax = plt.subplots()
    df_tx_f["Tiempo_Entrega_Limpio"].dropna().plot(
        kind="hist",
        bins=30,
        ax=ax
    )
    ax.set_xlabel("Días")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    # Estado del envío
    st.subheader("Estado del Envío")

    fig, ax = plt.subplots()
    df_tx_f["Estado_Envio"].value_counts().plot(
        kind="bar",
        ax=ax
    )
    ax.set_xlabel("Estado")
    ax.set_ylabel("Cantidad")
    st.pyplot(fig)

# ==================================================
# 🗣️ EDA FEEDBACK CLIENTES
# ==================================================
if seccion == "Feedback Clientes":

    st.title("🗣️ EDA – Feedback de Clientes")
    st.markdown(
        "Análisis de satisfacción, fricción y calidad percibida."
    )

    # KPIs NPS
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Promotores",
        int((df_fb["NPS_Grupo"] == "Promotor").sum())
    )

    col2.metric(
        "Pasivos",
        int((df_fb["NPS_Grupo"] == "Pasivo").sum())
    )

    col3.metric(
        "Detractores",
        int((df_fb["NPS_Grupo"] == "Detractor").sum())
    )

    # Rating producto
    st.subheader("Distribución del Rating de Producto")

    fig, ax = plt.subplots()
    df_fb["Rating_Producto"].dropna().plot(
        kind="hist",
        bins=5,
        ax=ax
    )
    ax.set_xlabel("Rating (1–5)")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    # Fricción del cliente
    st.subheader("Fricción del Cliente")

    fig, ax = plt.subplots()
    df_fb["friccion_cliente"].value_counts().plot(
        kind="bar",
        ax=ax
    )
    ax.set_xlabel("Fricción")
    ax.set_ylabel("Cantidad")
    st.pyplot(fig)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption(
    "EDA construido como fase previa al dashboard ejecutivo."
)
