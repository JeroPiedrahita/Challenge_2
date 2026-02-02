import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import unicodedata

# --- 1. CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="TechLogistics Senior Dashboard", layout="wide", page_icon="📈")

# Colores Corporativos TechLog
TECH_BLUE = "#1E3A8A"
TECH_SKY = "#0EA5E9"
TECH_DANGER = "#EF4444"
TECH_SUCCESS = "#10B981"

st.markdown(f"""
    <style>
    .main {{ background-color: #F8FAFC; }}
    .stMetric {{ background-color: white; border-radius: 10px; border-left: 5px solid {TECH_BLUE}; padding: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
    </style>
""", unsafe_allow_html=True)

# --- 2. FUNCIONES DE LIMPIEZA "VIVA" (Lógica de Consultoría) ---
def norm_text(x):
    if pd.isna(x): return "N/A"
    x = str(x).strip().upper()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

def clean_headers(df):
    df.columns = df.columns.str.strip().str.replace(r'[^\w\s]', '', regex=True)
    if 'SKUID' not in df.columns: df.rename(columns={df.columns[0]: 'SKU_ID'}, inplace=True)
    return df

@st.cache_data
def master_cleaning_process(inv_f, tx_f, fb_f):
    # A. Carga Blindada con detección de separador y codificación
    inv = clean_headers(pd.read_csv(inv_f, sep=None, engine='python', encoding='utf-8-sig'))
    tx = clean_headers(pd.read_csv(tx_f, sep=None, engine='python', encoding='utf-8-sig'))
    fb = clean_headers(pd.read_csv(fb_f, sep=None, engine='python', encoding='utf-8-sig'))

    # B. NORMALIZACIÓN FORZOSA DE IDs (Solución al KeyError)
    # Inventario: La primera columna DEBE ser SKU_ID
    if 'SKU_ID' not in inv.columns:
        inv.rename(columns={inv.columns[0]: 'SKU_ID'}, inplace=True)
    
    # Transacciones: 1ra columna SKU_ID, 2da columna Transaccion_ID
    if 'SKU_ID' not in tx.columns:
        tx.rename(columns={tx.columns[0]: 'SKU_ID'}, inplace=True)
    if 'Transaccion_ID' not in tx.columns:
        tx.rename(columns={tx.columns[1]: 'Transaccion_ID'}, inplace=True)

    # Feedback: La primera columna DEBE ser Feedback_ID, la segunda Transaccion_ID
    if 'Feedback_ID' not in fb.columns:
        fb.rename(columns={fb.columns[0]: 'Feedback_ID'}, inplace=True)
    if 'Transaccion_ID' not in fb.columns:
        fb.rename(columns={fb.columns[1]: 'Transaccion_ID'}, inplace=True)

    # C. Limpieza de Feedback (Ahora Feedback_ID ya existe garantizado)
    fb["Feedback_ID"] = fb["Feedback_ID"].astype(str).str.strip()
    fb = fb.drop_duplicates(subset=["Feedback_ID"])
    
    # Edad IQR (Datos numéricos)
    fb["Edad_Cliente"] = pd.to_numeric(fb["Edad_Cliente"], errors='coerce')
    q1, q3 = fb["Edad_Cliente"].quantile([0.25, 0.75])
    iqr = q3 - q1
    fb.loc[(fb["Edad_Cliente"] < q1 - 1.5*iqr) | (fb["Edad_Cliente"] > q3 + 1.5*iqr), "Edad_Cliente"] = np.nan
    
    # Ratings estrictos 1-5
    for r in ["Rating_Producto", "Rating_Logistica"]:
        if r in fb.columns:
            fb[r] = pd.to_numeric(fb[r], errors='coerce')
            fb.loc[(fb[r] < 1) | (fb[r] > 5), r] = np.nan

    # D. Limpieza de Inventario (Costos)
    inv["Costo_Unitario_USD"] = pd.to_numeric(inv["Costo_Unitario_USD"], errors='coerce')
    # Imputación por mediana de categoría para evitar sesgos de outliers
    if 'Categoria' in inv.columns:
        inv["Costo_Limpio"] = inv.groupby("Categoria")["Costo_Unitario_USD"].transform(
            lambda x: x.mask((x < x.quantile(0.05)) | (x > x.quantile(0.95)), x.median())
        )
    else:
        inv["Costo_Limpio"] = inv["Costo_Unitario_USD"]

    # E. Integración Master (Data Blending)
    # Unimos Ventas con Inventario por SKU
    df = tx.merge(inv, on="SKU_ID", how="left")
    # Unimos el resultado con Feedback por ID de Transacción
    df = df.merge(fb, on="Transaccion_ID", how="left")
    
    # F. La "Guillotina de Calidad" (Regla de múltiples nulos)
    # Filtramos filas que no aportan valor (muchos campos vacíos)
    cols_para_nulos = [c for c in ["Edad_Cliente", "Rating_Producto", "Satisfaccion_NPS", "Costo_Limpio"] if c in df.columns]
    if cols_para_nulos:
        df["nulos_count"] = df[cols_para_nulos].isnull().sum(axis=1)
        df = df[df["nulos_count"] < 2].copy()

    # G. Finalización de Financieros
    df["Ciudad_Destino"] = df["Ciudad_Destino"].apply(norm_text)
    df["Categoria"] = df["Categoria"].apply(norm_text)
    
    # Asegurar tipos para cálculos de margen
    precio = pd.to_numeric(df["Precio_Venta_Final"], errors='coerce')
    costo = pd.to_numeric(df["Costo_Limpio"], errors='coerce')
    cant = pd.to_numeric(df["Cantidad_Vendida"], errors='coerce')
    
    df["Margen_USD"] = (precio * cant) - (costo * cant)
    
    return df

# --- 3. UI - SIDEBAR Y FILTROS ---
st.sidebar.title("💎 TechLog Master BI")
with st.sidebar.expander("📂 Carga de Datos", expanded=True):
    f1 = st.file_uploader("Inventario", type="csv")
    f2 = st.file_uploader("Transacciones", type="csv")
    f3 = st.file_uploader("Feedback", type="csv")

if not (f1 and f2 and f3):
    st.info("👋 Bienvenido, Senior. Por favor, cargue los archivos CSV para activar el motor de análisis.")
    st.stop()

df = master_cleaning_process(f1, f2, f3)

# Filtros Dinámicos
st.sidebar.subheader("🎯 Segmentación")
sel_cat = st.sidebar.multiselect("Líneas de Producto", df["Categoria"].unique(), default=df["Categoria"].unique())
sel_city = st.sidebar.multiselect("Ciudades de Envío", df["Ciudad_Destino"].unique(), default=df["Ciudad_Destino"].unique())

df_view = df[(df["Categoria"].isin(sel_cat)) & (df["Ciudad_Destino"].isin(sel_city))]

# --- 4. DASHBOARD - VISUALIZACIÓN ---
tab_gen, tab_geo, tab_lab = st.tabs(["🏛️ Visión Ejecutiva", "📍 Análisis Geográfico", "🔬 Lab. de Insights"])

with tab_gen:
    st.markdown("### KPIs de Operación")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Venta Bruta", f"${df_view['Precio_Venta_Final'].sum():,.0f}")
    k2.metric("Margen Neto", f"${df_view['Margen_USD'].sum():,.0f}")
    k3.metric("NPS Avg", f"{round(df_view['Satisfaccion_NPS'].mean(), 1)}")
    k4.metric("Ciclo Entrega", f"{round(df_view['Tiempo_Entrega_Real'].mean(), 1)} d")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 Distribución por Categoría")
        fig_pie = px.pie(df_view, names="Categoria", values="Precio_Venta_Final", color_discrete_sequence=px.colors.qualitative.Prism, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        st.subheader("💰 Rentabilidad Operativa")
        fig_rent = px.histogram(df_view, x="Margen_USD", color="Categoria", barmode="overlay", nbins=30)
        st.plotly_chart(fig_rent, use_container_width=True)

with tab_geo:
    st.subheader("🌍 Análisis Exhaustivo de Ciudades")
    city_data = df_view.groupby("Ciudad_Destino").agg({
        "Margen_USD": "sum",
        "Tiempo_Entrega_Real": "mean",
        "Satisfaccion_NPS": "mean"
    }).sort_values("Margen_USD", ascending=True).reset_index()

    # Barras Horizontales de Margen
    fig_city = px.bar(city_data, x="Margen_USD", y="Ciudad_Destino", orientation='h',
                      color="Margen_USD", color_continuous_scale="RdBu", 
                      title="Margen Acumulado por Ciudad")
    st.plotly_chart(fig_city, use_container_width=True)

    # Tabla de Eficiencia Geográfica
    st.markdown("#### Ranking de Ciudades por NPS y Entrega")
    st.dataframe(city_data.style.background_gradient(cmap="Blues"), use_container_width=True)

with tab_lab:
    st.subheader("🧬 Correlaciones de Negocio")
    col1, col2 = st.columns([1, 3])
    with col1:
        x_axis = st.selectbox("Eje X (Causa)", ["Tiempo_Entrega_Real", "Edad_Cliente", "Precio_Venta_Final"])
        y_axis = st.selectbox("Eje Y (Efecto)", ["Satisfaccion_NPS", "Margen_USD"])
    with col2:
        fig_scat = px.scatter(df_view, x=x_axis, y=y_axis, color="Categoria", trendline="ols",
                              title=f"Impacto de {x_axis} en {y_axis}")
        st.plotly_chart(fig_scat, use_container_width=True)
