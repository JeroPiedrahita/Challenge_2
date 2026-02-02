import streamlit as st
import pandas as pd
import numpy as np
import unicodedata

# --------------------------------------------------
# 1. Configuración de la Aplicación
# --------------------------------------------------
st.set_page_config(page_title="TechLogistics Intelligence DSS", layout="wide", page_icon="📦")

# Estilo personalizado para métricas
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #007BFF; }
    .main { background-color: #f8f9fa; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 TechLogistics S.A.S. - Decision Support System")
st.info("Plataforma de Auditoría de Datos y Análisis de Rentabilidad Operativa")

# --------------------------------------------------
# 2. Funciones de Soporte (Limpieza y Normalización)
# --------------------------------------------------
def norm_text(x):
    if pd.isna(x): return x
    x = str(x).strip().lower()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

def get_nps_group(x):
    if pd.isna(x): return "No Opina"
    if x >= 9: return "Promotor"
    if x >= 7: return "Pasivo"
    return "Detractor"

def calculate_health(df_raw, df_clean):
    total_cells = df_clean.size
    null_pct = (df_clean.isna().sum().sum() / total_cells) * 100
    # Penalización por duplicados basada en el ID único si existe
    dups = len(df_raw) - len(df_clean)
    score = max(0, 100 - (null_pct * 1.5) - (dups / len(df_raw) * 100))
    return round(score, 1)

# --------------------------------------------------
# 3. Sidebar e Ingesta
# --------------------------------------------------
st.sidebar.header("📥 Carga de Activos")
inv_file = st.sidebar.file_uploader("Inventario Central (CSV)", type="csv")
tx_file = st.sidebar.file_uploader("Transacciones (CSV)", type="csv")
fb_file = st.sidebar.file_uploader("Feedback Clientes (CSV)", type="csv")

btn_limpieza = st.sidebar.button("🧹 Ejecutar Auditoría y Limpieza")

if btn_limpieza:
    if not all([inv_file, tx_file, fb_file]):
        st.sidebar.error("Error: Carga los 3 archivos para continuar.")
    else:
        # Carga inicial
        df_inv_raw = pd.read_csv(inv_file)
        df_tx_raw = pd.read_csv(tx_file)
        df_fb_raw = pd.read_csv(fb_file)

        # --- PROCESAMIENTO INVENTARIO ---
        df_inv = df_inv_raw.copy()
        df_inv["SKU_ID"] = df_inv["SKU_ID"].astype(str).str.strip().str.upper()
        df_inv["Categoria"] = df_inv["Categoria"].apply(norm_text).str.title()
        
        # Limpieza de Costos (Tratamiento del Outlier de $850k)
        df_inv["Costo_Unitario_USD"] = pd.to_numeric(df_inv["Costo_Unitario_USD"], errors="coerce")
        q_high = df_inv["Costo_Unitario_USD"].quantile(0.95)
        df_inv["Costo_Unitario_Limpio"] = df_inv["Costo_Unitario_USD"].mask(df_inv["Costo_Unitario_USD"] > q_high, df_inv.groupby("Categoria")["Costo_Unitario_USD"].transform("median"))
        
        df_inv = df_inv.drop_duplicates("SKU_ID")

        # --- PROCESAMIENTO TRANSACCIONES ---
        df_tx = df_tx_raw.copy()
        df_tx["SKU_ID"] = df_tx["SKU_ID"].astype(str).str.strip().str.upper()
        for c in ["Cantidad_Vendida", "Precio_Venta_Final", "Costo_Envio", "Tiempo_Entrega_Real"]:
            df_tx[c] = pd.to_numeric(df_tx[c], errors="coerce")
        df_tx = df_tx.drop_duplicates("Transaccion_ID")

        # --- PROCESAMIENTO FEEDBACK ---
        df_fb = df_fb_raw.copy()
        df_fb["Satisfaccion_NPS"] = pd.to_numeric(df_fb["Satisfaccion_NPS"], errors="coerce")
        df_fb["NPS_Grupo"] = df_fb["Satisfaccion_NPS"].apply(get_nps_group)
        map_sn = {"si":"Sí", "1":"Sí", "no":"No", "0":"No"}
        df_fb["Ticket_Soporte_Abierto"] = df_fb["Ticket_Soporte_Abierto"].astype(str).str.lower().map(map_sn).fillna("No")

        # Guardar en session_state
        st.session_state["data"] = {"inv": df_inv, "tx": df_tx, "fb": df_fb}
        st.session_state["health"] = {
            "inv": calculate_health(df_inv_raw, df_inv),
            "tx": calculate_health(df_tx_raw, df_tx),
            "fb": calculate_health(df_fb_raw, df_fb)
        }

# --------------------------------------------------
# 4. Visualización y Dashboard
# --------------------------------------------------
if "data" in st.session_state:
    data = st.session_state["data"]
    health = st.session_state["health"]

    # --- TABS PRINCIPALES ---
    tab1, tab2, tab3 = st.tabs(["🔍 Auditoría", "💰 Rentabilidad", "🚚 Logística & NPS"])

    with tab1:
        st.subheader("Estado de Salud de los Datos")
        c1, c2, c3 = st.columns(3)
        c1.metric("Salud Inventario", f"{health['inv']}%")
        c2.metric("Salud Transacciones", f"{health['tx']}%")
        c3.metric("Salud Feedback", f"{health['fb']}%")
        
        st.write("---")
        st.markdown("### Vista Previa de Datos Curados")
        dataset_sel = st.selectbox("Selecciona un dataset para inspeccionar:", ["Inventario", "Transacciones", "Feedback"])
        if dataset_sel == "Inventario": st.dataframe(data["inv"].head(50))
        elif dataset_sel == "Transacciones": st.dataframe(data["tx"].head(50))
        else: st.dataframe(data["fb"].head(50))

    with tab2:
        # Integración Master para Negocio
        df_master = data["tx"].merge(data["inv"], on="SKU_ID", how="left", indicator=True)
        df_master["SKU_Fantasma"] = df_master["_merge"] == "left_only"
        
        # Cálculos Financieros
        df_master["Ingreso_Total"] = df_master["Cantidad_Vendida"] * df_master["Precio_Venta_Final"]
        df_master["Costo_Total"] = (df_master["Cantidad_Vendida"] * df_master["Costo_Unitario_Limpio"]) + df_master["Costo_Envio"]
        df_master["Margen"] = df_master["Ingreso_Total"] - df_master["Costo_Total"]

        st.subheader("Análisis de Pérdidas y SKUs Fantasma")
        f1, f2 = st.columns(2)
        
        phantom_sales = df_master[df_master["SKU_Fantasma"]]
        f1.metric("Ventas Fantasma (Cant)", len(phantom_sales))
        f2.metric("Impacto en Ingresos", f"${phantom_sales['Ingreso_Total'].sum():,.2f} USD", delta_color="inverse")
        
        st.markdown("#### Distribución de Margen por Venta")
        st.bar_chart(df_master.groupby("Categoria")["Margen"].sum())

    with tab3:
        st.subheader("Correlación Logística vs Satisfacción")
        df_log = df_master.merge(data["fb"], on="Transaccion_ID", how="inner")
        
        col_l1, col_l2 = st.columns([2, 1])
        
        with col_l1:
            st.markdown("**Relación Tiempo de Entrega vs NPS**")
            st.scatter_chart(df_log, x="Tiempo_Entrega_Real", y="Satisfaccion_NPS", color="NPS_Grupo")
            
        with col_l2:
            st.markdown("**Tasa de Tickets por Categoría**")
            ticket_rate = df_log.groupby("Categoria")["Ticket_Soporte_Abierto"].apply(lambda x: (x == "Sí").mean() * 100)
            st.table(ticket_rate.sort_values(ascending=False))

else:
    st.warning("👋 Bienvenida, Junta Directiva. Por favor, cargue los archivos en el panel izquierdo para iniciar el análisis.")
