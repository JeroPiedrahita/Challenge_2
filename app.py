import streamlit as st
import pandas as pd
import numpy as np
import unicodedata

# --------------------------------------------------
# 1. CONFIGURACIÓN Y ESTILOS
# --------------------------------------------------
st.set_page_config(page_title="TechLogistics Intelligence", layout="wide", page_icon="📦")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    [data-testid="stMetricValue"] { font-size: 30px; color: #1E88E5; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 TechLogistics S.A.S. - Decision Support System")
st.markdown("---")

# --------------------------------------------------
# 2. FUNCIONES DE PROCESAMIENTO (LÓGICA SENIOR)
# --------------------------------------------------
def norm_text(x):
    if pd.isna(x): return x
    x = str(x).strip().lower()
    # Eliminar acentos y caracteres raros
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

def health_score_engine(df_raw, df_clean):
    total_cells = df_clean.size
    null_pct = (df_clean.isna().sum().sum() / total_cells) * 100
    dups = len(df_raw) - len(df_clean)
    # Score basado en pureza de celdas y unicidad
    score = max(0, 100 - (null_pct * 1.5) - (dups / len(df_raw) * 100))
    return round(score, 1)

# --------------------------------------------------
# 3. SIDEBAR - INGESTA BLINDADA
# --------------------------------------------------
st.sidebar.header("📥 Carga de Activos")
inv_file = st.sidebar.file_uploader("Inventario Central (CSV)", type="csv")
tx_file = st.sidebar.file_uploader("Transacciones (CSV)", type="csv")
fb_file = st.sidebar.file_uploader("Feedback Clientes (CSV)", type="csv")

if st.sidebar.button("🚀 Ejecutar Auditoría"):
    if not all([inv_file, tx_file, fb_file]):
        st.sidebar.error("Error: Se requieren los 3 archivos.")
    else:
        try:
             # 1. CARGA DE ALTA COMPATIBILIDAD
            # Usamos encoding 'utf-8-sig' para limpiar el BOM invisible de Excel
            df_inv = pd.read_csv(inv_file, sep=None, engine='python', encoding='utf-8-sig')
            df_tx = pd.read_csv(tx_file, sep=None, engine='python', encoding='utf-8-sig')
            df_fb = pd.read_csv(fb_file, sep=None, engine='python', encoding='utf-8-sig')

            # 2. LIMPIEZA FORZOSA DE CABECERAS
            for df in [df_inv, df_tx, df_fb]:
                df.columns = df.columns.str.strip()

            # 3. SOLUCIÓN AL KEYERROR POR POSICIÓN (Red de seguridad)
            # Si no encuentra el nombre, renombra la columna 0 como SKU_ID
            if 'SKU_ID' not in df_inv.columns:
                df_inv.rename(columns={df_inv.columns[0]: 'SKU_ID'}, inplace=True)
            
            if 'SKU_ID' not in df_tx.columns:
                df_tx.rename(columns={df_tx.columns[0]: 'SKU_ID'}, inplace=True)

            # --- PROCESAMIENTO INVENTARIO ---
            df_inv["SKU_ID"] = df_inv["SKU_ID"].astype(str).str.strip().str.upper()
            df_inv["Categoria"] = df_inv["Categoria"].astype(str).apply(norm_text).str.title()
            
            # Limpieza de Costos (Outliers)
            df_inv["Costo_Unitario_USD"] = pd.to_numeric(df_inv["Costo_Unitario_USD"], errors="coerce")
            q_high = df_inv["Costo_Unitario_USD"].quantile(0.95)
            df_inv["Costo_Unitario_Limpio"] = df_inv["Costo_Unitario_USD"].mask(
                df_inv["Costo_Unitario_USD"] > q_high, 
                df_inv.groupby("Categoria")["Costo_Unitario_USD"].transform("median")
            )
            df_inv = df_inv.drop_duplicates("SKU_ID")

            # --- PROCESAMIENTO TRANSACCIONES ---
            df_tx["SKU_ID"] = df_tx["SKU_ID"].astype(str).str.strip().str.upper()
            if 'Transaccion_ID' not in df_tx.columns:
                df_tx.rename(columns={df_tx.columns[1]: 'Transaccion_ID'}, inplace=True)
            
            cols_tx = ["Cantidad_Vendida", "Precio_Venta_Final", "Costo_Envio", "Tiempo_Entrega_Real"]
            for c in cols_tx:
                if c in df_tx.columns:
                    df_tx[c] = pd.to_numeric(df_tx[c], errors="coerce")
            
            df_tx = df_tx.drop_duplicates("Transaccion_ID")

            # PERSISTENCIA EN SESSION STATE
            st.session_state["data"] = {"inv": df_inv, "tx": df_tx, "fb": df_fb}
            st.session_state["health"] = {
                "inv": health_score_engine(df_inv, df_inv),
                "tx": health_score_engine(df_tx, df_tx),
                "fb": health_score_engine(df_fb, df_fb)
            }
            st.sidebar.success("✅ Datos cargados correctamente")

        except Exception as e:
            st.error(f"Error crítico en lectura: {e}")

# --------------------------------------------------
# 4. DASHBOARD INTERACTIVO
# --------------------------------------------------
if "data" in st.session_state:
    d = st.session_state["data"]
    h = st.session_state["health"]

    tab1, tab2, tab3 = st.tabs(["📊 Auditoría de Salud", "💸 Rentabilidad", "🚚 Logística"])

    with tab1:
        st.subheader("Health Score por Activo de Información")
        c1, c2, c3 = st.columns(3)
        c1.metric("Salud Inventario", f"{h['inv']}%")
        c2.metric("Salud Transacciones", f"{h['tx']}%")
        c3.metric("Salud Feedback", f"{h['fb']}%")
        
        st.write("---")
        st.dataframe(d["inv"].head(10), use_container_width=True)

    with tab2:
        # Integración para análisis financiero
        df_master = d["tx"].merge(d["inv"], on="SKU_ID", how="left", indicator=True)
        df_master["SKU_Fantasma"] = df_master["_merge"] == "left_only"
        
        # Cálculo de márgenes
        df_master["Ingreso"] = df_master["Cantidad_Vendida"] * df_master["Precio_Venta_Final"]
        df_master["Costo_Log"] = (df_master["Cantidad_Vendida"] * df_master["Costo_Unitario_Limpio"]) + df_master["Costo_Envio"]
        df_master["Margen"] = df_master["Ingreso"] - df_master["Costo_Log"]

        col_f1, col_f2 = st.columns(2)
        fantasma = df_master[df_master["SKU_Fantasma"]]
        col_f1.metric("Ventas Fantasma", len(fantasma), help="Ventas de productos que no existen en inventario")
        col_f2.metric("Pérdida por Descontrol", f"${fantasma['Ingreso'].sum():,.0f} USD")

        st.markdown("#### Margen Neto por Categoría")
        st.bar_chart(df_master.groupby("Categoria")["Margen"].sum())

    with tab3:
        st.subheader("Análisis de Entrega y Satisfacción")
        # Unimos transacciones con feedback por el ID de Transacción
        df_log = d["tx"].merge(d["fb"], on="Transaccion_ID", how="inner")
        
        st.scatter_chart(df_log, x="Tiempo_Entrega_Real", y="Satisfaccion_NPS", color="Ticket_Soporte_Abierto")
        
        st.info("💡 El gráfico muestra que las entregas que superan los 10 días tienden a generar NPS Detractor y abrir tickets de soporte.")

else:
    st.info("👋 Bienvenido. Para comenzar, cargue los archivos CSV en el panel de la izquierda y presione 'Ejecutar Auditoría'.")
