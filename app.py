import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import unicodedata

# 1. IDENTIDAD VISUAL CORPORATIVA
st.set_page_config(page_title="TechLogistics Analytics Pro", layout="wide")

# Colores institucionales: Azul Profundo, Acero y Alerta
TECH_BLUE = "#1E3A8A"
STEEL_GRAY = "#64748B"
SUCCESS_GREEN = "#10B981"
DANGER_RED = "#EF4444"

# 2. PROCESAMIENTO DE DATOS (INGENIERÍA DE CARACTERÍSTICAS)
def fix_headers(df):
    df.columns = df.columns.str.strip().str.replace(r'[^\w\s]', '', regex=True)
    if 'SKU_ID' not in df.columns:
        df.rename(columns={df.columns[0]: 'SKU_ID'}, inplace=True)
    return df

@st.cache_data
def process_data(inv_f, tx_f, fb_f):
    # Carga blindada
    inv = fix_headers(pd.read_csv(inv_f, sep=None, engine='python', encoding='utf-8-sig'))
    tx = fix_headers(pd.read_csv(tx_f, sep=None, engine='python', encoding='utf-8-sig'))
    fb = fix_headers(pd.read_csv(fb_f, sep=None, engine='python', encoding='utf-8-sig'))
    
    # Normalización de Llaves
    inv["SKU_ID"] = inv["SKU_ID"].astype(str).str.upper().str.strip()
    tx["SKU_ID"] = tx["SKU_ID"].astype(str).str.upper().str.strip()
    
    # Integración Master
    df = tx.merge(inv, on="SKU_ID", how="left")
    df = df.merge(fb, on="Transaccion_ID", how="left")
    
    # Casting numérico y limpieza de financieros
    cols = ["Precio_Venta_Final", "Costo_Unitario_USD", "Cantidad_Vendida", "Satisfaccion_NPS", "Tiempo_Entrega_Real"]
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')
    
    # Imputación de costos atípicos por mediana de categoría
    df["Costo_Unitario_USD"] = df["Costo_Unitario_USD"].fillna(df.groupby("Categoria")["Costo_Unitario_USD"].transform("median"))
    
    # Kpis Derivados
    df["Ingreso_Bruto"] = df["Cantidad_Vendida"] * df["Precio_Venta_Final"]
    df["Margen_Neto"] = df["Ingreso_Bruto"] - (df["Cantidad_Vendida"] * df["Costo_Unitario_USD"])
    df["Estado_Margen"] = np.where(df["Margen_Neto"] > 0, "Rentable", "Riesgo/Pérdida")
    
    return df

# 3. INTERFAZ DE USUARIO (UI/UX)
st.title("🚀 TechLogistics Executive Control")

st.sidebar.title("Configuración")
inv_f = st.sidebar.file_uploader("Inventario", type="csv")
tx_f = st.sidebar.file_uploader("Transacciones", type="csv")
fb_f = st.sidebar.file_uploader("Feedback", type="csv")

if not (inv_f and tx_f and fb_f):
    st.warning("⚠️ Esperando carga de archivos CSV para iniciar auditoría...")
    st.stop()

df_master = process_data(inv_f, tx_f, fb_f)

# FILTROS DE NEGOCIO
with st.sidebar:
    st.divider()
    cat_list = df_master["Categoria"].dropna().unique().tolist()
    sel_cat = st.multiselect("Categoría de Producto", cat_list, default=cat_list[:3])
    
    bod_list = df_master["Bodega_Origen"].dropna().unique().tolist()
    sel_bod = st.multiselect("Bodega de Origen", bod_list, default=bod_list)

df_filtrado = df_master[(df_master["Categoria"].isin(sel_cat)) & (df_master["Bodega_Origen"].isin(sel_bod))]

# 4. DASHBOARD DE INDICADORES (MÉTRICAS)
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Ingresos", f"${df_filtrado['Ingreso_Bruto'].sum():,.0f}", delta="Ventas Totales")
col_m2.metric("Margen Neto", f"${df_filtrado['Margen_Neto'].sum():,.0f}", delta=f"{round(df_filtrado['Margen_Neto'].mean(), 2)} avg")
col_m3.metric("NPS Satisfacción", f"{round(df_filtrado['Satisfaccion_NPS'].mean(), 1)} / 10")
col_m4.metric("Tiempo Entrega", f"{round(df_filtrado['Tiempo_Entrega_Real'].mean(), 1)} días")

# 5. VISUALIZACIONES ESTRATÉGICAS
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Rentabilidad por Categoría (USD)")
    fig_bar = px.bar(df_filtrado.groupby("Categoria")["Margen_Neto"].sum().reset_index(), 
                     x="Margen_Neto", y="Categoria", orientation='h',
                     color="Margen_Neto", color_continuous_scale="Blues")
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("🎯 Mix de Ventas por Estado de Riesgo")
    fig_pie = px.pie(df_filtrado, names="Estado_Margen", values="Ingreso_Bruto",
                     color="Estado_Margen", color_discrete_map={"Rentable": SUCCESS_GREEN, "Riesgo/Pérdida": DANGER_RED})
    st.plotly_chart(fig_pie, use_container_width=True)

# 6. LABORATORIO DE CORRELACIÓN (INSIGHTS)
st.subheader("🧬 Análisis de Correlación Dinámica")
cx1, cx2 = st.columns([1, 3])

with cx1:
    vx = st.selectbox("Eje X (Causa)", ["Tiempo_Entrega_Real", "Costo_Unitario_USD", "Cantidad_Vendida"])
    vy = st.selectbox("Eje Y (Efecto)", ["Satisfaccion_NPS", "Margen_Neto"])
    
with cx2:
    fig_scat = px.scatter(df_filtrado, x=vx, y=vy, color="Categoria", 
                          trendline="ols", title=f"Impacto de {vx} en {vy}")
    st.plotly_chart(fig_scat, use_container_width=True)

st.success("✅ Dashboard actualizado con éxito. El archivo requirements.txt es necesario para el despliegue.")
