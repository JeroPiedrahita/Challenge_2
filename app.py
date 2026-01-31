import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DEL DASHBOARD (Senior Level) ---
st.set_page_config(page_title="TechLogistics DSS", layout="wide")

st.title("📦 TechLogistics S.A.S. - Decision Support System")
st.markdown("---")

# --- BARRA LATERAL: CARGA DE DATOS ---
st.sidebar.header("📥 Ingesta de Datos")
st.sidebar.markdown("Sube los archivos CSV para iniciar la auditoría.")

# Cargadores de archivos según el ecosistema de datos [cite: 12, 13, 16]
file_inv = st.sidebar.file_uploader("1. Inventario Central (CSV)", type=["csv"])
file_log = st.sidebar.file_uploader("2. Transacciones Logística (CSV)", type=["csv"])
file_feed = st.sidebar.file_uploader("3. Feedback Clientes (CSV)", type=["csv"])

# --- FUNCIONES DE AUDITORÍA  ---
def calcular_salud(df):
    if df is None: return 0, 0, 0
    nulos = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()
    total_datos = df.size
    # Health Score: Penaliza nulos y duplicados 
    score = 100 - ((nulos + duplicados) / total_datos * 100)
    return round(score, 2), nulos, duplicados

# --- LÓGICA DE PROCESAMIENTO ---
if file_inv and file_log and file_feed:
    try:
        # Carga de datasets [cite: 11]
        df_inv = pd.read_csv(file_inv)
        df_log = pd.read_csv(file_log)
        df_feed = pd.read_csv(file_feed)

        st.sidebar.success("✅ Activos de información cargados")

        # Estructura de Navegación por Pestañas [cite: 119]
        tab_audit, tab_ops, tab_ia = st.tabs([
            "🔍 Fase 1: Auditoría", 
            "⚙️ Fase 2: Operaciones", 
            "🤖 Fase 3: Insights IA"
        ])

        with tab_audit:
            st.header("Auditoría de Calidad Inicial (Health Score)")
            st.info("Visualización del estado de los datos antes de la curaduría.")
            
            col1, col2, col3 = st.columns(3)
            
            # Análisis de Inventario [cite: 12]
            with col1:
                score, n, d = calcular_salud(df_inv)
                st.metric("Salud Inventario", f"{score}%")
                st.write(f"**Nulos:** {n} | **Duplicados:** {d}")
                st.dataframe(df_inv.head(5))

            # Análisis de Logística [cite: 13, 15]
            with col2:
                score, n, d = calcular_salud(df_log)
                st.metric("Salud Logística", f"{score}%")
                st.write(f"**Nulos:** {n} | **Duplicados:** {d}")
                st.dataframe(df_log.head(5))

            # Análisis de Feedback [cite: 16]
            with col3:
                score, n, d = calcular_salud(df_feed)
                st.metric("Salud Feedback", f"{score}%")
                st.write(f"**Nulos:** {n} | **Duplicados:** {d}")
                st.dataframe(df_feed.head(5))

        with tab_ops:
            st.warning("⚠️ Pendiente: Implementar Limpieza de Outliers e Integración (Merging)[cite: 27, 103].")

    except Exception as e:
        st.error(f"Error técnico al procesar archivos: {e} [cite: 55]")
else:
    st.info("👋 Bienvenida, Junta Directiva. Por favor, cargue los tres archivos en la barra lateral para proceder[cite: 9].")
