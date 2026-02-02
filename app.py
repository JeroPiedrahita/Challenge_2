import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
# Importamos las funciones de tu módulo de procesamiento
from Data_prossesing import clean_inventario, clean_transacciones, clean_feedback, merge_datasets

# 1. CONFIGURACIÓN E IDENTIDAD
st.set_page_config(page_title="TechLogistics Global Analytics", layout="wide", page_icon="🚀")

# Colores Corporativos
PRIMARY_BLUE = "#1E3A8A"
ACCENT_BLUE = "#3B82F6"
SUCCESS_GREEN = "#10B981"

st.markdown(f"""
    <style>
    .main {{ background-color: #f8fafc; }}
    .stMetric {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
    </style>
    """, unsafe_allow_html=True)

# 2. MOTOR DE CARGA Y NORMALIZACIÓN (Solución al KeyError)
@st.cache_data
def load_and_standardize(inv_f, tx_f, fb_f):
    # Carga inicial
    inv_r = pd.read_csv(inv_f)
    tx_r = pd.read_csv(tx_f)
    fb_r = pd.read_csv(fb_f)
    
    # MAPEADOR: Renombramos columnas para que coincidan con lo que espera Data_prossesing.py
    # Esto soluciona el error 'Tiempo_Entrega'
    tx_r = tx_r.rename(columns={'Tiempo_Entrega_Real': 'Tiempo_Entrega'})
    fb_r = fb_r.rename(columns={'Ticket_Soporte_Abierto': 'Ticket_Soporte'})
    
    # Ejecutamos tu lógica de Data_prossesing.py
    df_inv, log_inv = clean_inventario(inv_r)
    df_tx, log_tx = clean_transacciones(tx_r)
    df_fb, log_fb = clean_feedback(fb_r)
    
    # Unión final
    df_master, metrics = merge_datasets(df_inv, df_tx, df_fb)
    return df_master, metrics

# --- SIDEBAR ---
st.sidebar.title("📥 Panel de Control")
inv_file = st.sidebar.file_uploader("Hoja: Inventario", type="csv")
tx_file = st.sidebar.file_uploader("Hoja: Transacciones", type="csv")
fb_file = st.sidebar.file_uploader("Hoja: Feedback", type="csv")

if not (inv_file and tx_file and fb_file):
    st.warning("⚠️ Cargue los 3 archivos CSV para activar el motor de BI.")
    st.stop()

# Procesamiento
df, metrics = load_and_standardize(inv_file, tx_file, fb_file)

# Filtros Dinámicos
with st.sidebar:
    st.divider()
    cat_filter = st.multiselect("Filtrar por Categoría", df["Categoria"].unique(), default=df["Categoria"].unique())
    bodega_filter = st.multiselect("Filtrar por Bodega", df["Bodega_Origen"].unique(), default=df["Bodega_Origen"].unique())

df_filt = df[(df["Categoria"].isin(cat_filter)) & (df["Bodega_Origen"].isin(bodega_filter))]

# 3. DASHBOARD EJECUTIVO
st.title("🚀 TechLogistics Executive Intelligence")
st.subheader("Análisis Integral de Supply Chain y Satisfacción")

# KPIs de Alto Nivel
k1, k2, k3, k4 = st.columns(4)
total_rev = df_filt["Precio_Venta_Final"].sum()
avg_margin = df_filt["Margen_Pct"].mean()
nps_score = df_filt["Satisfaccion_NPS"].mean()

k1.metric("Ingresos Totales", f"${total_rev:,.0f}", "USD")
k2.metric("Margen Neto Promedio", f"{avg_margin:.1f}%", f"{df_filt['Margen_USD'].sum():,.0f} Total")
k3.metric("NPS (Customer Health)", f"{nps_score:.1f}", "pts")
k4.metric("Ventas Fantasma", metrics['phantom_sales'], "SKUs no registrados", delta_color="inverse")

st.divider()

# --- LAS 5 GRÁFICAS ESTRATÉGICAS ---

# FILA 1
c1, c2 = st.columns([6, 4])

with c1:
    # 1. Gráfica Financiera: Margen por Categoría y Bodega
    st.markdown("### 💰 Estructura de Rentabilidad")
    fig1 = px.bar(df_filt, x="Categoria", y="Margen_USD", color="Bodega_Origen",
                  barmode="group", text_auto='.2s', template="plotly_white",
                  color_discrete_sequence=px.colors.qualitative.Prism)
    st.plotly_chart(fig1, use_container_width=True)

with c2:
    # 2. Gráfica de Correlación: Logística vs Satisfacción
    st.markdown("### ⏱️ Impacto de Entrega en NPS")
    fig2 = px.scatter(df_filt, x="Tiempo_Entrega", y="Satisfaccion_NPS", 
                      size="Cantidad_Vendida", color="Categoria",
                      trendline="ols", template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)

# FILA 2
c3, c4 = st.columns(2)

with c3:
    # 3. Gráfica de Inventario: Mapa de Calor de Stock
    st.markdown("### 📦 Distribución de Inventario Crítico")
    fig3 = px.treemap(df_filt, path=[px.Constant("Global"), 'Bodega_Origen', 'Categoria'], 
                      values='Stock_Actual', color='Dias_Sin_Revision',
                      color_continuous_scale='RdYlGn_r', 
                      title="Volumen de Stock (Color: Días desde última revisión)")
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    # 4. Gráfica de Feedback: Calidad por Categoría
    st.markdown("### ⭐ Auditoría de Calidad (Rating)")
    fig4 = px.box(df_filt, x="Categoria", y="Rating_Producto", color="Ticket_Soporte",
                  notched=True, title="Distribución de Ratings y Soporte Abierto")
    st.plotly_chart(fig4, use_container_width=True)

# FILA 3 (Ancho Completo)
# 5. Tendencia Temporal: Desempeño Diario
st.markdown("### 📈 Evolución Histórica de Ventas")
df_filt['Fecha_Venta'] = pd.to_datetime(df_filt['Fecha_Venta'])
resumen_diario = df_filt.groupby('Fecha_Venta')[['Precio_Venta_Final', 'Margen_USD']].sum().reset_index()

fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=resumen_diario['Fecha_Venta'], y=resumen_diario['Precio_Venta_Final'],
                         mode='lines', name='Ingresos Brutos', line=dict(color=ACCENT_BLUE, width=3)))
fig5.add_trace(go.Scatter(x=resumen_diario['Fecha_Venta'], y=resumen_diario['Margen_USD'],
                         mode='lines', name='Margen Neto', fill='tozeroy', line=dict(color=SUCCESS_GREEN)))
fig5.update_layout(template="plotly_white", hovermode="x unified")
st.plotly_chart(fig5, use_container_width=True)

# AUDITORÍA TÉCNICA
with st.expander("🛠️ Detalles Técnicos de Integridad (Data Cleaning Log)"):
    col_a, col_b = st.columns(2)
    col_a.write("**Métricas de Salud del Dataset:**")
    col_a.json(metrics)
    if st.checkbox("Mostrar Tabla de Datos Normalizados"):
        st.dataframe(df_filt.head(50))
