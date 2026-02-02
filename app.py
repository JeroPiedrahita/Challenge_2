
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import unicodedata
import plotly.express as px
from data_processing import (
    clean_inventario,
    clean_transacciones,
    clean_feedback,
    resumen_limpieza
)


# --------------------------------------------------
# Configuración general
# --------------------------------------------------
st.set_page_config(
    page_title="EDA Operacional – TechLog",
    layout="wide"
)

st.title("📦 EDA Operacional – TechLog")
st.markdown(
    "Auditoría de datos, integración y análisis de riesgo para una operación **Tech + Logistics**."
)

# --------------------------------------------------
# Funciones auxiliares
# --------------------------------------------------
def norm(x):
    if pd.isna(x):
        return x
    x = str(x).strip().lower()
    return unicodedata.normalize("NFKD", x).encode("ascii","ignore").decode("utf-8")

def nps_grupo(x):
    if pd.isna(x): return np.nan
    if x >= 9: return "Promotor"
    if x >= 7: return "Pasivo"
    return "Detractor"

def health_report(df_raw, df_clean):
    pct_nulos = df_clean.isna().mean() * 100
    duplicados = len(df_raw) - len(df_raw.drop_duplicates())

    num = df_clean.select_dtypes(include=np.number)
    outliers = ((num - num.mean()).abs() > 3 * num.std()).sum().sum()

    health = max(
        0,
        100 - (
            pct_nulos.mean() * 0.4 +
            (duplicados / len(df_raw)) * 100 * 0.2 +
            (outliers / max(1, num.size)) * 100 * 0.4
        )
    )

    return {
        "health_score": round(health, 1),
        "pct_nulos": pct_nulos,
        "duplicados": duplicados,
        "outliers": int(outliers)
    }

# --------------------------------------------------
# Sidebar – Ingesta
# --------------------------------------------------
st.sidebar.title("Carga de Datos")

inv_file = st.sidebar.file_uploader("Inventario", type="csv")
tx_file  = st.sidebar.file_uploader("Transacciones", type="csv")
fb_file  = st.sidebar.file_uploader("Feedback Clientes", type="csv")

if st.sidebar.button("🧹 Ejecutar Limpieza"):

    if not all([inv_file, tx_file, fb_file]):
        st.error("Debes cargar los tres archivos.")
        st.stop()

    # ---------------- Ingesta RAW ----------------
    df_inv_raw = pd.read_csv(inv_file)
    df_tx_raw  = pd.read_csv(tx_file)
    df_fb_raw  = pd.read_csv(fb_file)

    # ---------------- Limpieza ----------------
    df_inv = clean_inventario(df_inv_raw)
    df_tx  = clean_transacciones(df_tx_raw)
    df_fb  = clean_feedback(df_fb_raw)

    # ---------------- Reportes de limpieza ----------------
    st.session_state["rep_inv"] = resumen_limpieza(df_inv_raw, df_inv)
    st.session_state["rep_tx"]  = resumen_limpieza(df_tx_raw, df_tx)
    st.session_state["rep_fb"]  = resumen_limpieza(df_fb_raw, df_fb)

    # ---------------- Guardar dataframes ----------------
    st.session_state["df_inv_raw"] = df_inv_raw
    st.session_state["df_tx_raw"]  = df_tx_raw
    st.session_state["df_fb_raw"]  = df_fb_raw

    st.session_state["df_inv"] = df_inv
    st.session_state["df_tx"]  = df_tx
    st.session_state["df_fb"]  = df_fb

# --------------------------------------------------
# Validación
# --------------------------------------------------
if "df_inv" not in st.session_state:
    st.info("Carga los archivos y ejecuta la limpieza.")
    st.stop()

df_inv = st.session_state["df_inv"]
df_tx  = st.session_state["df_tx"]
df_fb  = st.session_state["df_fb"]

df_inv_raw = st.session_state.get("df_inv_raw")
df_tx_raw  = st.session_state.get("df_tx_raw")
df_fb_raw  = st.session_state.get("df_fb_raw")
# --------------------------------------------------
# Auditoría visual
# --------------------------------------------------

# --------------------------------------------------
# Integración
# --------------------------------------------------
df_master = (
    df_tx
    .merge(df_inv, on="SKU_ID", how="left", indicator=True)
    .merge(df_fb, on="Transaccion_ID", how="left")
)

df_master["sku_fantasma"] = df_master["_merge"] == "left_only"
df_master["Ingreso"] = df_master["Cantidad_Vendida"] * df_master["Precio_Venta_Final"]
df_master["Costo_Total"] = df_master["Cantidad_Vendida"] * df_master["Costo_Unitario_Limpio"] + df_master["Costo_Envio"]
df_master["Margen_Utilidad"] = df_master["Ingreso"] - df_master["Costo_Total"]
df_master["Brecha_Entrega"] = df_master["Tiempo_Entrega_Limpio"] - df_master["Lead_Time_Limpio"]

st.sidebar.header("🎛️ Filtros")


fecha_min = df_master["Fecha_Venta"].min()
fecha_max = df_master["Fecha_Venta"].max()

rango_fechas = st.sidebar.date_input(
    "Rango de fechas",
    value=(fecha_min, fecha_max),
    min_value=fecha_min,
    max_value=fecha_max
)

# Filtros básicos
bodegas = st.sidebar.multiselect(
    "Bodega de Origen",
    options=sorted(df_master["Bodega_Origen"].dropna().unique()),
    default=sorted(df_master["Bodega_Origen"].dropna().unique())
)

ciudades = st.sidebar.multiselect(
    "Ciudad Destino",
    options=sorted(df_master["Ciudad_Destino_Limpia"].dropna().unique()),
    default=sorted(df_master["Ciudad_Destino_Limpia"].dropna().unique())
)

canales = st.sidebar.multiselect(
    "Canal de Venta",
    options=sorted(df_master["Canal_Venta"].dropna().unique()),
    default=sorted(df_master["Canal_Venta"].dropna().unique())
)

refrescar = st.sidebar.button("🔄 Refrescar Análisis")

# Aplicar filtros
df_f = df_master[
    (df_master["Bodega_Origen"].isin(bodegas)) &
    (df_master["Fecha_Venta"].between(
        pd.to_datetime(rango_fechas[0]),
        pd.to_datetime(rango_fechas[1])
    ))
]



tab1, tab2, tab3, tab4 = st.tabs(
    ["🧪 Auditoría", "⚙️ Operaciones", "👥 Cliente", "🤖 Insights IA"]
)


#-----------------------------------------------------
#  Auditoria
#----------------------------------------------------

with tab1:
    if "df_inv_raw" not in st.session_state:
        st.warning("Ejecuta la limpieza para ver la auditoría.")
        st.stop()


    st.subheader("🔎 Transparencia de Limpieza – Inventario")

    resumen = resumen_limpieza(df_inv_raw, df_inv)

    


    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Filas Originales", resumen["Filas iniciales"])
    col2.metric("Filas Finales", resumen["Filas finales"])
    col3.metric("Duplicados Eliminados", resumen["Duplicados"])
    col4.metric(
        "Salud de Datos (%)",
        f'{resumen["Salud de datos (%)"]}%'
    )

    st.divider()
    st.subheader("📂 Vista Antes vs Después")
    
    dataset = st.selectbox(
        "Selecciona el dataset",
        ["Inventario", "Transacciones", "Feedback"]
    )
    
    if dataset == "Inventario":
        df_raw = st.session_state["df_inv_raw"]
        df_clean = df_inv
    elif dataset == "Transacciones":
        df_raw = st.session_state["df_tx_raw"]
        df_clean = df_tx
    else:
        df_raw = st.session_state["df_fb_raw"]
        df_clean = df_fb
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ❌ Antes de la Limpieza")
        st.dataframe(df_raw.head(100), use_container_width=True)
    
    with col2:
        st.markdown("### ✅ Después de la Limpieza")
        st.dataframe(df_clean.head(100), use_container_width=True)
with tab2:

    # --------------------------------------------------
    # KPIs Ejecutivos
    # --------------------------------------------------
    st.subheader("📊 KPIs Operacionales")
    
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Ingresos Totales (USD)", f"${df_f['Ingreso'].sum():,.0f}")
    col2.metric("Margen Total (USD)", f"${df_f['Margen_Utilidad'].sum():,.0f}")
    
    margen_pct = (df_f["Margen_Utilidad"].sum() / df_f["Ingreso"].sum()) * 100
    col3.metric("Margen Total (%)", f"{margen_pct:.1f}%")
    
    col4.metric(
        "Ventas con SKU Fantasma (%)",
        f"{df_f['sku_fantasma'].mean() * 100:.1f}%"
    )
    
    # --------------------------------------------------
    # Análisis interactivo de correlaciones
    # --------------------------------------------------
    st.subheader("🔍 Relación entre Variables Operativas y de Negocio")
    
    st.markdown(
        """
        Explora cómo las variables logísticas y comerciales se relacionan entre sí.
        Cambia los ejes para descubrir patrones ocultos y cuellos de botella.
        """
    )
    
    variables_numericas = {
        "Tiempo de Entrega": "Tiempo_Entrega_Limpio",
        "Brecha de Entrega": "Brecha_Entrega",
        "Margen de Utilidad": "Margen_Utilidad",
        "Ingreso por Venta": "Ingreso",
        "Satisfacción (NPS)": "Satisfaccion_NPS",
        "Rating Logística": "Rating_Logistica",
        "Rating Producto": "Rating_Producto"
    }
    
    colx, coly, colc = st.columns(3)
    
    x_var_label = colx.selectbox("Eje X", variables_numericas.keys(), index=0)
    y_var_label = coly.selectbox("Eje Y", variables_numericas.keys(), index=4)
    
    color_var = colc.selectbox(
        "Color por",
        ["Canal_Venta", "Bodega_Origen", "Estado_Envio"],
        index=0
    )
    
    x_var = variables_numericas[x_var_label]
    y_var = variables_numericas[y_var_label]
    
    fig = px.scatter(
        df_f,
        x=x_var,
        y=y_var,
        color=color_var,
        hover_data=[
            "SKU_ID",
            "Ciudad_Destino_Limpia",
            "Canal_Venta"
        ],
        opacity=0.6,
        trendline="ols",
        title=f"{y_var_label} vs {x_var_label}"
    )
    
    fig.update_layout(
        template="plotly_white",
        height=500,
        legend_title_text=color_var.replace("_", " ")
    )
    
    # ... después de fig.update_layout()
    st.plotly_chart(fig, use_container_width=True, key="grafico_dispersion_operativo")
    
    # --- AQUÍ ESTÁ LA CORRECCIÓN ---
    # Calculamos la correlación de Pearson entre las dos variables seleccionadas
    # Usamos .dropna() para que no de error si hay valores nulos
    # 1. Calculamos la correlación
    corr = df_f[x_var].corr(df_f[y_var])
    
    # 2. Definimos la etiqueta de intensidad antes del markdown
    if abs(corr) > 0.7:
        intensidad = "fuerte"
    elif abs(corr) > 0.3:
        intensidad = "moderada"
    else:
        intensidad = "débil"
    
    # 3. Mostramos el markdown limpio
    st.markdown(
        f"""
        **📌 Interpretación rápida**
    
        La correlación entre **{x_var_label}** y **{y_var_label}** es de  
        **{corr:.2f}**, lo que sugiere una relación **{intensidad}**.
    
        Esto permite analizar cómo las variables operativas
        influyen entre sí dentro del negocio.
        """
    )
    
    
    st.subheader("💡 ¿Dónde se gana y dónde se pierde dinero?")
    
    fig = px.box(
        df_f,
        x="Bodega_Origen",
        y="Margen_Utilidad",
        color="Bodega_Origen",
        title="Distribución de Margen por Bodega"
    )
    
    fig.update_layout(
        template="plotly_white",
        showlegend=False
    )
    
    # ... busca el px.box para el Margen_Utilidad
    st.plotly_chart(fig, use_container_width=True, key="grafico_cajas_rentabilidad")
    
    # --------------------------------------------------
    # Rentabilidad
    # --------------------------------------------------
    st.subheader("💰 Rentabilidad por Bodega")
    
    margen_bodega_df = (
        df_f
        .groupby("Bodega_Origen", as_index=False)["Margen_Utilidad"]
        .mean()
        .sort_values("Margen_Utilidad")
    )
    
    fig = px.bar(
        margen_bodega_df,
        y="Bodega_Origen",
        x="Margen_Utilidad",
        color="Bodega_Origen",
        orientation="h",
        title="Margen Promedio por Bodega (USD)"
    )
    
    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        xaxis_title="Margen promedio (USD)",
        yaxis_title="Bodega de Origen"
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        key="grafico_rentabilidad_bodega"
    )
    # --------------------------------------------------
    # Logística vs Satisfacción
    # --------------------------------------------------
    st.subheader("🚚 Logística y Satisfacción")
    
    fig = px.scatter(
        df_f,
        x="Tiempo_Entrega_Limpio",
        y="Satisfaccion_NPS",
        color="Bodega_Origen",
        opacity=0.4,
        title="Relación entre Tiempo de Entrega y Satisfacción (NPS)",
        labels={
            "Tiempo_Entrega_Limpio": "Tiempo de Entrega (días)",
            "Satisfaccion_NPS": "NPS"
        }
    )
    
    fig.update_layout(
        template="plotly_white"
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        key="grafico_logistica_satisfaccion"
    )
    
    # --------------------------------------------------
    # Riesgo Operativo
    # --------------------------------------------------
    # ---------------- Riesgo Operativo (preparación datos) ----------------
    riesgo_df = (
        df_f
        .assign(ticket_bin=df_f["Ticket_Soporte_Abierto"] == "Sí")
        .groupby("Bodega_Origen", as_index=False)["ticket_bin"]
        .mean()
        .rename(columns={"ticket_bin": "Tasa_Tickets"})
    )
    st.subheader("⚠️ Riesgo Operativo por Bodega")
    
    fig = px.bar(
        riesgo_df,
        x="Bodega_Origen",
        y="Tasa_Tickets",
        color="Bodega_Origen",
        title="Riesgo Operativo por Bodega"
    )
    
    fig.update_layout(
        template="plotly_white",
        showlegend=False,
        yaxis_tickformat=".0%",
        yaxis_title="Tasa de Tickets de Soporte",
        xaxis_title="Bodega de Origen"
    )
    
    st.plotly_chart(
        fig,
        use_container_width=True,
        key="grafico_riesgo_bodega"
    )


with tab3:
    st.subheader("Satisfacción del Cliente")

    fig = px.box(
        df_f,
        x="Bodega_Origen",
        y="Satisfaccion_NPS",
        color="Bodega_Origen",
        title="Distribución de NPS por Bodega"
    )

    fig.update_layout(template="plotly_white", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


with tab4:
    st.subheader("🤖 Insights Generados por IA")

    if st.button("🧠 Analizar con IA"):
        resumen = {
            "filas": len(df_f),
            "ingresos": df_f["Ingreso"].sum(),
            "margen": df_f["Margen_Utilidad"].sum(),
            "riesgo_promedio": (df_f["Ticket_Soporte_Abierto"] == "Sí").mean()
        }

        prompt = f"""
        Analiza el siguiente resumen operativo y genera 3 insights claros
        y accionables para un gerente logístico:

        {resumen}
        """

        # aquí llamas a Groq / Llama-3
        st.info("🔍 Analizando datos filtrados…")

