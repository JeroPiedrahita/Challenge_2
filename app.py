import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="TechLogistics DSS", layout="wide")

st.title("📦 TechLogistics S.A.S. - Sistema de Soporte a la Decisión")
st.markdown("---")

# --- BARRA LATERAL PARA CARGA DINÁMICA ---
st.sidebar.header("📥 Ingesta de Activos")
st.sidebar.write("Como Consultor Senior, cargue los tres datasets para iniciar.")

# Los archivos se suben aquí (No están precargados)
file_inv = st.sidebar.file_uploader("1. Inventario Central (CSV)", type=["csv"])
file_log = st.sidebar.file_uploader("2. Transacciones Logística (CSV)", type=["csv"])
file_feed = st.sidebar.file_uploader("3. Feedback Clientes (CSV)", type=["csv"])

# --- FUNCIÓN DE AUDITORÍA (REQUERIMIENTO FASE 1) ---
def auditoria_calidad(df):
    if df is None: return 0, 0, 0
    
    total_celdas = df.size
    nulos = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()
    
    # Cálculo del Health Score (Penalización por datos sucios)
    # Se reporta % de nulidad y duplicados según la guía [cite: 20]
    pct_nulos = (nulos / total_celdas) * 100
    score = 100 - (pct_nulos + (duplicados / len(df) * 100))
    
    return round(max(0, score), 2), nulos, duplicados

# --- CONTROL DE FLUJO ---
if file_inv and file_log and file_feed:
    # Lectura de los archivos subidos por el usuario
    df_inv = pd.read_csv(file_inv)
    df_log = pd.read_csv(file_log)
    df_feed = pd.read_csv(file_feed)
    
    st.sidebar.success("✅ Datos recibidos correctamente")

    # Creación de pestañas según el protocolo [cite: 119]
    tab1, tab2, tab3 = st.tabs(["🔍 Auditoría de Calidad", "⚙️ Operaciones (Merge)", "🤖 IA Insights"])

    with tab1:
        st.header("Fase 1: Health Score Inicial (The Raw Reality)")
        st.info("Métricas de calidad antes de la curaduría profunda[cite: 19].")
        
        c1, c2, c3 = st.columns(3)
        
        # Auditoría de Inventario
        with c1:
            score, n, d = auditoria_calidad(df_inv)
            st.metric("Salud Inventario", f"{score}/100")
            st.write(f"**Nulos:** {n} | **Duplicados:** {d}")
            st.dataframe(df_inv.head(5))
            
        # Auditoría de Logística
        with c2:
            score, n, d = auditoria_calidad(df_log)
            st.metric("Salud Logística", f"{score}/100")
            st.write(f"**Nulos:** {n} | **Duplicados:** {d}")
            st.dataframe(df_log.head(5))
            
        # Auditoría de Feedback
        with c3:
            score, n, d = auditoria_calidad(df_feed)
            st.metric("Salud Feedback", f"{score}/100")
            st.write(f"**Nulos:** {n} | **Duplicados:** {d}")
            st.dataframe(df_feed.head(5))

    with tab2:
        st.subheader("Fase 2: Integración de Datos")
        st.warning("Listo para procesar. En el siguiente paso realizaremos el 'Left Join' para detectar SKUs Fantasma[cite: 28, 94].")

else:
    # Mensaje inicial si no hay archivos
    st.info("👋 Por favor, suba los tres archivos CSV en el panel de la izquierda para comenzar el análisis.")
    st.image("https://via.placeholder.com/800x200.png?text=Esperando+Activos+de+Información", use_column_width=True)
