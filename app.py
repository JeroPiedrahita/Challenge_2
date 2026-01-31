import streamlit as st
import pandas as pd

# 1. Configuración básica
st.set_page_config(page_title="TechLogistics DSS", layout="wide")

st.title("📦 TechLogistics: Diagnóstico de Carga")

# 2. Sidebar con instrucciones claras
st.sidebar.header("📥 Panel de Carga")
st.sidebar.markdown("Sube los archivos CSV del reto para activar el Dashboard.")

f_inv = st.sidebar.file_uploader("1. Inventario", type=["csv"])
f_log = st.sidebar.file_uploader("2. Logística", type=["csv"])
f_feed = st.sidebar.file_uploader("3. Feedback", type=["csv"])

# 3. Lógica de verificación
if not f_inv or not f_log or not f_feed:
    st.warning("🕒 Esperando archivos...")
    st.info("""
    **Instrucciones para que funcione:**
    1. Ve a la barra lateral izquierda.
    2. Sube el archivo `inventario_central_v2.csv`[cite: 12].
    3. Sube el archivo `transacciones_logistica_v2.csv`[cite: 13].
    4. Sube el archivo `feedback_clientes_v2.csv`[cite: 16].
    """)
    
    # Verificador de estado para el usuario
    col_a, col_b, col_c = st.columns(3)
    col_a.write(f"Inventario: {'✅' if f_inv else '❌'}")
    col_b.write(f"Logística: {'✅' if f_log else '❌'}")
    col_c.write(f"Feedback: {'✅' if f_feed else '❌'}")

else:
    # Si los tres están cargados, procedemos
    try:
        df_inv = pd.read_csv(f_inv)
        df_log = pd.read_csv(f_log)
        df_feed = pd.read_csv(f_feed)
        
        st.success("🎉 ¡Todos los archivos detectados! Iniciando Auditoría...")
        
        # Pestaña de Auditoría (Requerimiento Fase 1) [cite: 18, 19]
        tab_audit, tab_limpieza = st.tabs(["🔍 Fase 1: Auditoría", "🧹 Fase 2: Limpieza"])
        
        with tab_audit:
            st.header("Salud de los Datos (The Raw Reality)") [cite: 10]
            c1, c2, c3 = st.columns(3)
            
            with c1:
                st.subheader("Inventario")
                st.write(f"Filas: {len(df_inv)}")
                st.dataframe(df_inv.head(5))
            
            with c2:
                st.subheader("Logística")
                st.write(f"Filas: {len(df_log)}")
                st.dataframe(df_log.head(5))
                
            with c3:
                st.subheader("Feedback")
                st.write(f"Filas: {len(df_feed)}")
                st.dataframe(df_feed.head(5))
                
    except Exception as e:
        st.error(f"Hubo un error al leer los archivos: {e}")
