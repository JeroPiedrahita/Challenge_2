import streamlit as st
import pandas as pd
import io

# Configuración profesional [cite: 114]
st.set_page_config(page_title="TechLogistics DSS", layout="wide")

st.title("📦 TechLogistics: Sistema de Soporte a la Decisión")
st.markdown("---")

# --- BARRA LATERAL PARA CARGA DE ARCHIVOS [cite: 117] ---
st.sidebar.header("📁 Carga de Datos")

file_inv = st.sidebar.file_uploader("Subir Inventario (CSV)", type=["csv"])
file_log = st.sidebar.file_uploader("Subir Logística (CSV)", type=["csv"])
file_feed = st.sidebar.file_uploader("Subir Feedback (CSV)", type=["csv"])

# --- FUNCIÓN DE AUDITORÍA (HEALTH SCORE) [cite: 19, 20] ---
def calcular_health_score(df):
    if df is None: return 0
    nulos = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()
    total_celdas = df.size
    # Penalizamos nulos y duplicados sobre el total de datos [cite: 20]
    score = 100 - ((nulos + duplicados) / total_celdas * 100)
    return round(score, 2), nulos, duplicados

# --- LÓGICA PRINCIPAL ---
if file_inv and file_log and file_feed:
    # Leer archivos subidos
    df_inv = pd.read_csv(file_inv)
    df_log = pd.read_csv(file_log)
    df_feed = pd.read_csv(file_feed)

    st.sidebar.success("✅ Todos los archivos cargados")

    # Organización por TABS como pide el reto [cite: 119]
    tab_audit, tab_ops, tab_ia = st.tabs(["🔍 Auditoría Inicial", "⚙️ Procesamiento", "🤖 Recomendaciones IA"])

    with tab_audit:
        st.header("Análisis de Calidad (The Raw Reality) [cite: 10]")
        col1, col2, col3 = st.columns(3)
        
        datos = [
            ("Inventario", df_inv, col1),
            ("Logística", df_log, col2),
            ("Feedback", df_feed, col3)
        ]

        for nombre, df, col in datos:
            score, nulos, dups = calcular_health_score(df)
            with col:
                st.subheader(nombre)
                st.metric("Health Score", f"{score}%")
                st.write(f"**Nulos detectados:** {nulos} [cite: 20]")
                st.write(f"**Duplicados:** {dups} [cite: 20]")
                st.dataframe(df.head(10)) # Vista previa del "caos" [cite: 4]
else:
    st.info("👋 Bienvenido, Consultor. Por favor, sube los **3 archivos CSV** en la barra lateral para comenzar el análisis.")
    st.warning("⚠️ El sistema requiere los tres archivos para realizar la integridad referencial (Merging) más adelante.")
