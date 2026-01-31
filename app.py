import streamlit as st
import pandas as pd

# 1. Configuración de página (Debe ser la primera instrucción de Streamlit)
st.set_page_config(page_title="TechLogistics DSS", layout="wide")

st.title("📦 TechLogistics: Dashboard de Consultoría")
st.markdown("---")

# 2. Sidebar para cargar los archivos
st.sidebar.header("📥 Carga de Datos")
st.sidebar.write("Sube los 3 archivos CSV para activar el análisis.")

f_inv = st.sidebar.file_uploader("1. Inventario Central", type="csv")
f_log = st.sidebar.file_uploader("2. Logística", type="csv")
f_feed = st.sidebar.file_uploader("3. Feedback", type="csv")

# 3. Función de Health Score
def calcular_salud(df):
    if df is not None:
        nulos = df.isnull().sum().sum()
        dups = df.duplicated().sum()
        total = df.size
        # Salud = 100% menos el impacto de errores
        score = 100 - ((nulos + dups) / total * 100)
        return round(score, 2), nulos, dups
    return 0, 0, 0

# 4. Lógica de visualización
if f_inv and f_log and f_feed:
    # Leer archivos
    df_inv = pd.read_csv(f_inv)
    df_log = pd.read_csv(f_log)
    df_feed = pd.read_csv(f_feed)

    st.success("✅ ¡Datos cargados exitosamente!")

    # Pestañas
    t1, t2 = st.tabs(["🔍 Auditoría de Calidad", "⚙️ Próximos Pasos"])

    with t1:
        st.header("Fase 1: Health Score Inicial")
        c1, c2, c3 = st.columns(3)

        # Inventario
        s1, n1, d1 = calcular_salud(df_inv)
        with c1:
            st.metric("Salud Inventario", f"{s1}%")
            st.write(f"Nulos: {n1} | Dups: {d1}")
            st.dataframe(df_inv.head(5))

        # Logística
        s2, n2, d2 = calcular_salud(df_log)
        with c2:
            st.metric("Salud Logística", f"{s2}%")
            st.write(f"Nulos: {n2} | Dups: {d2}")
            st.dataframe(df_log.head(5))

        # Feedback
        s3, n3, d3 = calcular_salud(df_feed)
        with c3:
            st.metric("Salud Feedback", f"{s3}%")
            st.write(f"Nulos: {n3} | Dups: {d3}")
            st.dataframe(df_feed.head(5))
            
    with t2:
        st.info("La Fase 2 consistirá en unir estos datos y limpiar los costos atípicos.")

else:
    st.warning("🚦 Sistema a la espera de archivos. Por favor, súbelos en la barra lateral.")
