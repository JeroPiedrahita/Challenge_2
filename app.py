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
# Carga de datos
# --------------------------------------------------
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

df_inv = load_data("data/inventario_limpio.csv")
df_tx  = load_data("data/transacciones_limpio.csv")
df_fb  = load_data("data/feedback_limpio.csv")

# --------------------------------------------------
# Sidebar – Navegación
# --------------------------------------------------
st.sidebar.title("EDA – Navegación")

seccion = st.sidebar.radio(
    "Selecciona el módulo:",
    [
        "Inventario",
        "Transacciones",
        "Feedback Clientes"
    ]
)

# ==================================================
# 📦 EDA INVENTARIO
# ==================================================
if seccion == "Inventario":

    st.title("📦 EDA – Inventario")
    st.markdown("Estado del inventario y calidad del dato operativo.")

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
        "Costo Mediano (USD)",
        f"${df_inv['Costo_Unitario_Limpio'].median():,.2f}"
    )

    # Distribución de costos
    st.subheader("Distribución del Costo Unitario Limpio")

    fig, ax = plt.subplots()
    df_inv["Costo_Unitario_Limpio"].dropna().plot(
        kind="hist",
        bins=30,
        ax=ax
    )
    ax.set_xlabel("Costo Unitario USD")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    # Lead time
    st.subheader("Distribución del Lead Time (días)")

    fig, ax = plt.subplots()
    df_inv["Lead_Time_Limpio"].dropna().plot(
        kind="hist",
        bins=25,
        ax=ax
    )
    ax.set_xlabel("Días")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

    # Stock vs Punto de Reorden
    st.subheader("Stock Actual vs Punto de Reorden")

    fig, ax = plt.subplots()
    ax.scatter(
        df_inv["Punto_Reorden"],
        df_inv["Stock_Actual"],
        alpha=0.6
    )
    ax.set_xlabel("Punto de Reorden")
    ax.set_ylabel("Stock Actual")
    st.pyplot(fig)

# ==================================================
# 🚚 EDA TRANSACCIONES
# ==================================================
if seccion == "Transacciones":

    st.title("🚚 EDA – Transacciones")
    st.markdown("Comportamiento de ventas y desempeño logístico.")

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
        "Transacciones",
        df_tx_f["Transaccion_ID"].nunique()
    )

    col2.metric(
        "Unidades Vendidas",
        int(df_tx_f["Cantidad_Vendida"].sum())
    )

    col3.metric(
        "Tiempo Entrega Mediano (días)",
        int(df_tx_f["Tiempo_Entrega_Limpio"].median())
    )

    # Distribución tiempo entrega
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

    # Canal de venta
    st.subheader("Canal de Venta")

    fig, ax = plt.subplots()
    df_tx_f["Canal_Venta"].value_counts().plot(
        kind="bar",
        ax=ax
    )
    ax.set_xlabel("Canal")
    ax.set_ylabel("Cantidad")
    st.pyplot(fig)

# ==================================================
# 🗣️ EDA FEEDBACK CLIENTES
# ==================================================
if seccion == "Feedback Clientes":

    st.title("🗣️ EDA – Feedback de Clientes")
    st.markdown("Satisfacción del cliente y fricción post-venta.")

    # KPIs
    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Rating Producto (Mediana)",
        float(df_fb["Rating_Producto"].median())
    )

    col2.metric(
        "Rating Logística (Mediana)",
        float(df_fb["Rating_Logistica"].median())
    )

    col3.metric(
        "Edad Mediana Cliente",
        int(df_fb["Edad_Cliente"].median())
    )

    # Distribución Rating Producto
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

    # NPS
    st.subheader("Distribución NPS")

    fig, ax = plt.subplots()
    df_fb["NPS_Grupo"].value_counts().plot(
        kind="bar",
        ax=ax
    )
    ax.set_xlabel("Grupo NPS")
    ax.set_ylabel("Cantidad")
    st.pyplot(fig)

    # Tickets de soporte
    st.subheader("Tickets de Soporte")

    fig, ax = plt.subplots()
    df_fb["Ticket_Soporte_Abierto"].value_counts().plot(
        kind="bar",
        ax=ax
    )
    ax.set_xlabel("Ticket Abierto")
    ax.set_ylabel("Cantidad")
    st.pyplot(fig)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.caption(
    "EDA basado en datasets limpios – fase previa a dashboard ejecutivo."
)
