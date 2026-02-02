import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import unicodedata

# --------------------------------------------------
# 1. CONFIGURACIÓN E IDENTIDAD CORPORATIVA
# --------------------------------------------------
st.set_page_config(page_title="TechLogistics Executive Dashboard", layout="wide", page_icon="📊")

# Paleta de colores TechLog
colors = ["#1E3A8A", "#3B82F6", "#64748B", "#94A3B8", "#CBD5E1"]

def apply_custom_style():
    st.markdown(f"""
        <style>
        .main {{ background-color: #F8FAFC; }}
        .stMetric {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        [data-testid="stSidebar"] {{ background-color: #1E293B; color: white; }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_style()

# --------------------------------------------------
# 2. FUNCIONES DE PROCESAMIENTO
# --------------------------------------------------
def clean_header(df):
    df.columns = df.columns.str.strip().str.replace(r'[^\w\s]', '', regex=True)
    if 'SKU_ID' not in df.columns:
        df.rename(columns={df.columns[0]: 'SKU_ID'}, inplace=True)
    return df

def norm_text(x):
    if pd.isna(x): return "N/A"
    x = str(x).strip().upper()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

# --------------------------------------------------
# 3. CARGA Y FILTROS (SIDEBAR)
# --------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2769/2769331.png", width=100)
st.sidebar.title("TechLog Control Center")

with st.sidebar.expander("📂 Ingesta de Datos", expanded=True):
    inv_file = st.file_uploader("Inventario", type="csv")
    tx_file = st.file_uploader("Transacciones", type="csv")
    fb_file = st.file_uploader("Feedback", type="csv")

if not (inv_file and tx_file and fb_file):
    st.info("👋 Bienvenida, Junta Directiva. Por favor, cargue los activos de información para iniciar la auditoría.")
    st.stop()

# Procesamiento silencioso al cargar
@st.cache_data
def load_and_clean(inv_f, tx_f, fb_f):
    inv = clean_header(pd.read_csv(inv_f, sep=None, engine='python', encoding='utf-8-sig'))
    tx = clean_header(pd.read_csv(tx_f, sep=None, engine='python', encoding='utf-8-sig'))
    fb = clean_header(pd.read_csv(fb_f, sep=None, engine='python', encoding='utf-8-sig'))
    
    # Limpieza básica para cruce
    inv["SKU_ID"] = inv["SKU_ID"].astype(str).str.strip().str.upper()
    tx["SKU_ID"] = tx["SKU_ID"].astype(str).str.strip().str.upper()
    
    # Integración Master
    master = tx.merge(inv, on="SKU_ID", how="left")
    master = master.merge(fb, on="Transaccion_ID", how="left")
    
    # Conversiones numéricas
    cols_num = ["Precio_Venta_Final", "Costo_Unitario_USD", "Cantidad_Vendida", "Satisfaccion_NPS", "Tiempo_Entrega_Real"]
    for c in cols_num:
        if c in master.columns:
            master[c] = pd.to_numeric(master[c], errors='coerce')
    
    master["Margen_USD"] = master["Precio_Venta_Final"] - master["Costo_Unitario_USD"]
    return master

df_all = load_and_clean(inv_file, tx_file, fb_file)

# FILTROS GLOBALES
st.sidebar.subheader("🎯 Filtros de Operación")
selected_cat = st.sidebar.multiselect("Categoría de Producto", options=df_all["Categoria"].unique(), default=df_all["Categoria"].unique())
selected_bodega = st.sidebar.multiselect("Bodega de Origen", options=df_all["Bodega_Origen"].unique(), default=df_all["Bodega_Origen"].unique())

df = df_all[(df_all["Categoria"].isin(selected_cat)) & (df_all["Bodega_Origen"].isin(selected_bodega))]

# --------------------------------------------------
# 4. DASHBOARD - MÉTRICAS CLAVE
# --------------------------------------------------
m1, m2, m3, m4 = st.columns(4)
m1.metric("Ingresos Totales", f"${df['Precio_Venta_Final'].sum():,.0f}")
m2.metric("Margen Promedio", f"${df['Margen_USD'].mean():,.2f}")
m3.metric("NPS General", round(df["Satisfaccion_NPS"].mean(), 1))
m4.metric("Eficiencia Entrega", f"{df['Tiempo_Entrega_Real'].mean():,.1f} días")

st.markdown("---")

# --------------------------------------------------
# 5. ANÁLISIS VISUAL PROFESIONAL
# --------------------------------------------------
c1, c2 = st.columns(2)

with c1:
    st.subheader("📦 Distribución por Categoría")
    # Gráfico de Pastel (Pie Chart)
    fig_pie = px.pie(df, names="Categoria", values="Precio_Venta_Final", 
                     color_discrete_sequence=colors, hole=0.4)
    fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("💰 Margen por Bodega")
    # Gráfico de Barras Horizontales
    fig_bar = px.bar(df.groupby("Bodega_Origen")["Margen_USD"].sum().reset_index(), 
                     x="Margen_USD", y="Bodega_Origen", orientation='h',
                     color_discrete_sequence=[colors[0]])
    fig_bar.update_layout(xaxis_title="Margen Total (USD)", yaxis_title="")
    st.plotly_chart(fig_bar, use_container_width=True)

# --------------------------------------------------
# 6. CORRELACIONES DINÁMICAS
# --------------------------------------------------
st.subheader("🧬 Laboratorio de Correlaciones")
st.markdown("Analice cómo interactúan las variables críticas de la operación.")

col_corr1, col_corr2 = st.columns([1, 3])

with col_corr1:
    var_x = st.selectbox("Variable eje X", options=["Tiempo_Entrega_Real", "Precio_Venta_Final", "Costo_Unitario_USD"])
    var_y = st.selectbox("Variable eje Y", options=["Satisfaccion_NPS", "Margen_USD", "Cantidad_Vendida"])
    color_var = st.selectbox("Segmentar por", options=["Categoria", "Bodega_Origen", "Ciudad_Destino"])

with col_corr2:
    fig_scatter = px.scatter(df, x=var_x, y=var_y, color=color_var,
                             trendline="ols", color_discrete_sequence=px.colors.qualitative.Prism,
                             title=f"Relación: {var_x} vs {var_y}")
    st.plotly_chart(fig_scatter, use_container_width=True)

# --------------------------------------------------
# 7. TABLA DE AUDITORÍA
# --------------------------------------------------
with st.expander("📑 Ver Datos Maestro (Auditados)"):
    st.dataframe(df.style.highlight_max(axis=0, color='#E2E8F0'), use_container_width=True)
