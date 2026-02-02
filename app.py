import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from data_processing import clean_inventario, clean_transacciones, clean_feedback, merge_datasets

# CONFIGURACIÓN PROFESIONAL
st.set_page_config(page_title="TechLogistics Global Intelligence", layout="wide")

# Estilo de CSS para KPIs
st.markdown("""
    <style>
    [data-testid="stMetricValue"] { font-size: 28px; color: #1E3A8A; }
    .stAlert { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_process(inv_f, tx_f, fb_f):
    # Carga y limpieza usando tu módulo externo
    inv_r = pd.read_csv(inv_f)
    tx_r = pd.read_csv(tx_f)
    fb_r = pd.read_csv(fb_f)
    
    df_inv, _ = clean_inventario(inv_r)
    df_tx, _ = clean_transacciones(tx_r)
    df_fb, _ = clean_feedback(fb_r)
    
    return merge_datasets(df_inv, df_tx, df_fb)

# --- SIDEBAR & FILTROS ---
st.sidebar.header("📥 Carga de Datos Operativos")
inv_file = st.sidebar.file_uploader("Inventario (CSV)", type="csv")
tx_file = st.sidebar.file_uploader("Transacciones (CSV)", type="csv")
fb_file = st.sidebar.file_uploader("Feedback (CSV)", type="csv")

if not (inv_file and tx_file and fb_file):
    st.info("👋 Bienvenido. Por favor carga los archivos para generar el reporte ejecutivo.")
    st.stop()

df, metrics = load_and_process(inv_file, tx_file, fb_file)

with st.sidebar:
    st.divider()
    st.subheader("🎯 Filtros Ejecutivos")
    categorias = st.multiselect("Categorías", df["Categoria"].unique(), default=df["Categoria"].unique())
    bodegas = st.multiselect("Bodegas", df["Bodega_Origen"].unique(), default=df["Bodega_Origen"].unique())
    
df_filt = df[(df["Categoria"].isin(categorias)) & (df["Bodega_Origen"].isin(bodegas))]

# --- DASHBOARD PRINCIPAL ---
st.title("📊 Business Intelligence: TechLogistics")

# 1. KPIs DE ALTO IMPACTO
m1, m2, m3, m4 = st.columns(4)
m1.metric("Revenue Total", f"${df_filt['Precio_Venta_Final'].sum():,.0f}")
m2.metric("Margen Promedio", f"{df_filt['Margen_Pct'].mean():.1f}%")
m3.metric("CSAT (NPS)", f"{df_filt['Satisfaccion_NPS'].mean():.0f} pts")
m4.metric("SKUs Fantasma", f"{metrics['phantom_sales']}", delta="Riesgo de Inventario", delta_color="inverse")

st.divider()

# --- BLOQUE DE GRÁFICAS (5 Reportes Clave) ---

row1_c1, row1_c2 = st.columns(2)

with row1_c1:
    # GRÁFICA 1: Rentabilidad por Categoría (Barras compuestas)
    st.subheader("💰 Rentabilidad por Categoría")
    fig1 = px.bar(df_filt, x="Categoria", y="Margen_USD", color="Bodega_Origen",
                 title="Margen USD acumulado por Categoria y Bodega",
                 barmode="group", template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)

with row1_c2:
    # GRÁFICA 2: Eficiencia de Entrega vs Satisfacción (Scatter)
    st.subheader("⏱️ Logística vs Satisfacción")
    fig2 = px.scatter(df_filt, x="Tiempo_Entrega", y="Satisfaccion_NPS", 
                     color="Categoria", size="Cantidad_Vendida",
                     hover_data=["SKU_ID"], trendline="lowess",
                     title="Impacto del tiempo de entrega en el NPS")
    st.plotly_chart(fig2, use_container_width=True)

row2_c1, row2_c2 = st.columns(2)

with row2_c1:
    # GRÁFICA 3: Estado Crítico de Inventario (Treemap)
    st.subheader("📦 Análisis de Inventario y Rotación")
    fig3 = px.treemap(df_filt, path=["Bodega_Origen", "Categoria"], values="Stock_Actual",
                     color="Dias_Sin_Revision", color_continuous_scale='RdYlGn_r',
                     title="Volumen de Stock por Bodega (Color: Días sin revisión)")
    st.plotly_chart(fig3, use_container_width=True)

with row2_c2:
    # GRÁFICA 4: Calidad del Servicio (Radar o Boxplot)
    st.subheader("⭐ Distribución de Ratings")
    fig4 = px.box(df_filt, x="Categoria", y="Rating_Producto", color="Ticket_Soporte",
                 title="Ratings de Producto y Necesidad de Soporte",
                 points="all", notched=True)
    st.plotly_chart(fig4, use_container_width=True)

# GRÁFICA 5: Análisis de Tendencia Temporal (Si hay fechas)
st.subheader("📈 Tendencia de Ventas y Márgenes")
df_filt['Fecha_Venta'] = pd.to_datetime(df_filt['Fecha_Venta'])
resumen_tiempo = df_filt.set_index('Fecha_Venta').resample('D')[['Precio_Venta_Final', 'Margen_USD']].sum().reset_index()

fig5 = go.Figure()
fig5.add_trace(go.Scatter(x=resumen_tiempo['Fecha_Venta'], y=resumen_tiempo['Precio_Venta_Final'], name="Venta Bruta"))
fig5.add_trace(go.Scatter(x=resumen_tiempo['Fecha_Venta'], y=resumen_tiempo['Margen_USD'], name="Margen USD", fill='tozeroy'))
fig5.update_layout(title="Desempeño Diario de Ingresos y Utilidad", template="plotly_white")
st.plotly_chart(fig5, use_container_width=True)

# --- SECCIÓN DE AUDITORÍA ---
with st.expander("🛠️ Reporte de Integridad de Datos (Módulo de Limpieza)"):
    st.write(f"Ventas de SKUs no registrados: {metrics['phantom_sales']}")
    st.write(f"Ingresos en riesgo por SKUs fantasma: ${metrics['phantom_revenue']:,.2f}")
    if st.checkbox("Ver datos crudos filtrados"):
        st.dataframe(df_filt)
