import streamlit as st
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="TechLogistics DSS - Senior Consultant", layout="wide")

st.title("📦 TechLogistics S.A.S. - Decision Support System")
st.markdown("---")

# --- FUNCIONES DE CARGA Y AUDITORÍA ---
@st.cache_data
def load_data():
    try:
        df_inv = pd.read_csv("inventario_central_v2.csv")
        df_log = pd.read_csv("transacciones_logistica_v2.csv")
        df_feed = pd.read_csv("feedback_clientes_v2.csv")
        return df_inv, df_log, df_feed
    except FileNotFoundError as e:
        st.error(f"Error: No se encontró un archivo. {e}")
        return None, None, None

def calcular_health_score(df):
    if df is None: return 0, {}
    
    total_celdas = df.size
    nulos = df.isnull().sum().sum()
    duplicados = df.duplicated().sum()
    
    # El Health Score baja por nulos y duplicados
    pct_nulos = (nulos / total_celdas) * 100
    pct_duplicados = (duplicados / len(df)) * 100
    
    score = max(0, 100 - (pct_nulos + (pct_duplicados * 2))) # Duplicados penalizan más
    
    return round(score, 1), {
        "Nulidad (%)": round(pct_nulos, 2),
        "Duplicados": duplicados,
        "Total Filas": len(df)
    }

# --- EJECUCIÓN PRINCIPAL ---
inv_raw, log_raw, feed_raw = load_data()

if inv_raw is not None:
    # Sidebar para navegación
    menu = st.sidebar.radio("Navegación", ["1. Auditoría de Calidad", "2. Limpieza e Integración", "3. Análisis Estratégico"])

    if menu == "1. Auditoría de Calidad":
        st.header("🔍 Auditoría de Calidad Inicial (Raw Reality)")
        st.info("Estado de los datos antes de la intervención de consultoría.")

        col1, col2, col3 = st.columns(3)
        
        datasets = [
            ("Inventario", inv_raw, col1),
            ("Logística", log_raw, col2),
            ("Feedback", feed_raw, col3)
        ]

        for nombre, df, columna in datasets:
            score, mets = calcular_health_score(df)
            with columna:
                st.subheader(nombre)
                st.metric("Health Score", f"{score}/100")
                st.write(f"**Registros:** {mets['Total Filas']}")
                st.write(f"**Nulidad:** {mets['Nulidad (%)']}%")
                st.write(f"**Duplicados:** {mets['Duplicados']}")
                st.dataframe(df.head(5))

else:
    st.warning("Por favor, asegúrate de que los archivos CSV estén en la misma carpeta que app.py")
