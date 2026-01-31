"""
Dashboard TechLogistics - Challenge 02
Sistema de Soporte a la Decisión
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(__file__))
from modules.data_processing import (
    calculate_health_score, clean_inventario, clean_transacciones,
    clean_feedback, merge_datasets
)

# Configuración de página
st.set_page_config(
    page_title="TechLogistics DSS",
    page_icon="📊",
    layout="wide"
)

# CSS simple
st.markdown("""
<style>
    .big-title {font-size: 2rem; font-weight: bold; color: #1f77b4;}
    .metric-box {background: #f0f2f6; padding: 1rem; border-radius: 5px; margin: 0.5rem 0;}
</style>
""", unsafe_allow_html=True)


# Inicializar session state
if 'data_processed' not in st.session_state:
    st.session_state.data_processed = False
if 'df_final' not in st.session_state:
    st.session_state.df_final = None


def call_groq_api(prompt, api_key):
    """Llama a Groq API para obtener conclusiones"""
    try:
        import requests
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": "Eres un consultor de analytics experto."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000
            },
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        else:
            return f"Error: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


# ===== SIDEBAR =====
st.sidebar.markdown("## ⚙️ Configuración")

# API Key de Groq
st.sidebar.markdown("### 🤖 Groq API Key")
groq_api_key = st.sidebar.text_input(
    "API Key",
    type="password",
    help="Obtén tu API key en https://console.groq.com"
)

st.sidebar.markdown("---")

# Carga de archivos
st.sidebar.markdown("### 📂 Cargar Datos")

inventario_file = st.sidebar.file_uploader(
    "1. inventario_central_v2.csv",
    type=['csv']
)

transacciones_file = st.sidebar.file_uploader(
    "2. transacciones_logistica_v2.csv",
    type=['csv']
)

feedback_file = st.sidebar.file_uploader(
    "3. feedback_clientes_v2.csv",
    type=['csv']
)

# Botón procesar
if inventario_file and transacciones_file and feedback_file:
    if st.sidebar.button("🚀 Procesar Datos", type="primary"):
        with st.spinner("Procesando datos..."):
            
            # Cargar datos
            df_inv = pd.read_csv(inventario_file)
            df_trans = pd.read_csv(transacciones_file)
            df_feed = pd.read_csv(feedback_file)
            
            # Health Score ANTES
            health_before = {
                'inventario': calculate_health_score(df_inv, 'Inventario'),
                'transacciones': calculate_health_score(df_trans, 'Transacciones'),
                'feedback': calculate_health_score(df_feed, 'Feedback')
            }
            
            # Limpiar
            df_inv_clean, log_inv = clean_inventario(df_inv)
            df_trans_clean, log_trans = clean_transacciones(df_trans)
            df_feed_clean, log_feed = clean_feedback(df_feed)
            
            # Health Score DESPUÉS
            health_after = {
                'inventario': calculate_health_score(df_inv_clean, 'Inventario'),
                'transacciones': calculate_health_score(df_trans_clean, 'Transacciones'),
                'feedback': calculate_health_score(df_feed_clean, 'Feedback')
            }
            
            # Integrar
            df_final, metrics = merge_datasets(df_inv_clean, df_trans_clean, df_feed_clean)
            
            # Guardar en session state
            st.session_state.df_final = df_final
            st.session_state.health_before = health_before
            st.session_state.health_after = health_after
            st.session_state.logs = {
                'inventario': log_inv,
                'transacciones': log_trans,
                'feedback': log_feed
            }
            st.session_state.metrics = metrics
            st.session_state.data_processed = True
            
        st.sidebar.success("✅ Datos procesados!")

st.sidebar.markdown("---")

# Filtros (solo si hay datos)
if st.session_state.data_processed:
    st.sidebar.markdown("### 🎯 Filtros")
    
    df = st.session_state.df_final
    
    # Filtro de fechas
    if 'Fecha_Venta' in df.columns:
        min_date = df['Fecha_Venta'].min().date()
        max_date = df['Fecha_Venta'].max().date()
        date_range = st.sidebar.date_input(
            "Rango de Fechas",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
    
    # Filtro de categoría
    categorias = ['Todas'] + sorted(df['Categoria'].dropna().unique().tolist())
    selected_cat = st.sidebar.selectbox("Categoría", categorias)
    
    # Filtro de bodega
    bodegas = ['Todas'] + sorted(df['Bodega_Origen'].dropna().unique().tolist())
    selected_bodega = st.sidebar.selectbox("Bodega", bodegas)
    
    # Aplicar filtros
    df_filtered = df.copy()
    
    if len(date_range) == 2:
        df_filtered = df_filtered[
            (df_filtered['Fecha_Venta'].dt.date >= date_range[0]) &
            (df_filtered['Fecha_Venta'].dt.date <= date_range[1])
        ]
    
    if selected_cat != 'Todas':
        df_filtered = df_filtered[df_filtered['Categoria'] == selected_cat]
    
    if selected_bodega != 'Todas':
        df_filtered = df_filtered[df_filtered['Bodega_Origen'] == selected_bodega]
    
    st.sidebar.info(f"Registros: {len(df_filtered):,}")
    
    if st.sidebar.button("🔄 Refrescar Análisis"):
        st.rerun()
else:
    df_filtered = None


# ===== CONTENIDO PRINCIPAL =====

# Título
st.markdown('<p class="big-title">📊 Sistema de Soporte a la Decisión - TechLogistics</p>', 
            unsafe_allow_html=True)
st.markdown("**Challenge 02** | Fundamentos en Ciencia de Datos | EAFIT")
st.markdown("---")

# Tabs principales
if st.session_state.data_processed and df_filtered is not None:
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔍 Auditoría", 
        "📊 Operaciones", 
        "👥 Cliente",
        "🤖 IA Insights"
    ])
    
    # ===== TAB 1: AUDITORÍA =====
    with tab1:
        st.markdown("## 🔍 Auditoría de Calidad de Datos")
        
        # Health Scores
        st.markdown("### Health Score - Antes vs Después")
        
        col1, col2, col3 = st.columns(3)
        
        for col, ds_name, emoji in zip(
            [col1, col2, col3],
            ['inventario', 'transacciones', 'feedback'],
            ['📦', '🚚', '⭐']
        ):
            with col:
                before = st.session_state.health_before[ds_name]
                after = st.session_state.health_after[ds_name]
                
                st.markdown(f"#### {emoji} {before['dataset_name']}")
                
                # Métrica de Health Score
                delta = after['health_score'] - before['health_score']
                st.metric(
                    "Health Score",
                    f"{after['health_score']:.1f}%",
                    f"+{delta:.1f}%"
                )
                
                st.markdown(f"""
                **Antes:**
                - Registros: {before['total_records']:,}
                - Nulos: {before['total_nulls']}
                - Duplicados: {before['duplicates']}
                
                **Después:**
                - Registros: {after['total_records']:,}
                - Nulos: {after['total_nulls']}
                - Duplicados: {after['duplicates']}
                """)
        
        st.markdown("---")
        
        # Logs de limpieza
        st.markdown("### 📝 Acciones de Limpieza Realizadas")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Inventario:**")
            for log in st.session_state.logs['inventario']:
                st.markdown(f"✓ {log}")
        
        with col2:
            st.markdown("**Transacciones:**")
            for log in st.session_state.logs['transacciones']:
                st.markdown(f"✓ {log}")
        
        with col3:
            st.markdown("**Feedback:**")
            for log in st.session_state.logs['feedback']:
                st.markdown(f"✓ {log}")
        
        st.markdown("---")
        
        # Métricas de integración
        st.markdown("### 🔗 Métricas de Integración")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Dataset Final", f"{st.session_state.metrics['total_records']:,} registros")
        
        with col2:
            st.metric("Ventas Fantasma", f"{st.session_state.metrics['phantom_sales']:,}")
        
        with col3:
            st.metric("Revenue Fantasma", f"${st.session_state.metrics['phantom_revenue']:,.0f}")
    
    
    # ===== TAB 2: OPERACIONES =====
    with tab2:
        st.markdown("## 📊 Análisis Operacional")
        
        # Pregunta 1: Márgenes Negativos
        st.markdown("### 💸 1. Fuga de Capital - Márgenes Negativos")
        
        negative_margin = df_filtered[df_filtered['Margen_USD'] < 0]
        total_loss = negative_margin['Margen_USD'].sum()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Pérdida Total", f"${total_loss:,.0f}")
        with col2:
            st.metric("Ventas Negativas", f"{len(negative_margin):,}")
        with col3:
            pct = (abs(total_loss) / df_filtered['Precio_Venta_Final'].sum() * 100) if len(df_filtered) > 0 else 0
            st.metric("% de Ingresos", f"{pct:.2f}%")
        
        if len(negative_margin) > 0:
            # Gráfica por categoría
            by_cat = negative_margin.groupby('Categoria')['Margen_USD'].sum().sort_values()
            
            fig1 = px.bar(
                x=by_cat.values,
                y=by_cat.index,
                orientation='h',
                title="Pérdidas por Categoría",
                labels={'x': 'Pérdida (USD)', 'y': 'Categoría'},
                color=by_cat.values,
                color_continuous_scale='Reds'
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        st.markdown("---")
        
        # Pregunta 2: Crisis Logística
        st.markdown("### 🚚 2. Crisis Logística")
        
        # Solo registros con NPS
        df_logistics = df_filtered[df_filtered['Satisfaccion_NPS'].notna()]
        
        if len(df_logistics) > 0:
            by_city = df_logistics.groupby('Ciudad_Destino').agg({
                'Tiempo_Entrega': 'mean',
                'Satisfaccion_NPS': 'mean',
                'Transaccion_ID': 'count'
            }).reset_index()
            by_city.columns = ['Ciudad', 'Tiempo_Prom', 'NPS_Prom', 'Transacciones']
            
            fig2 = px.scatter(
                by_city,
                x='Tiempo_Prom',
                y='NPS_Prom',
                size='Transacciones',
                text='Ciudad',
                title='Tiempo de Entrega vs NPS por Ciudad',
                labels={'Tiempo_Prom': 'Tiempo Entrega (días)', 'NPS_Prom': 'NPS Promedio'}
            )
            fig2.update_traces(textposition='top center')
            st.plotly_chart(fig2, use_container_width=True)
            
            # Tabla de ciudades críticas
            worst_cities = by_city.nsmallest(3, 'NPS_Prom')
            st.markdown("**Ciudades Críticas (menor NPS):**")
            st.dataframe(worst_cities, use_container_width=True)
        
        st.markdown("---")
        
        # Pregunta 3: Ventas Fantasma
        st.markdown("### 👻 3. Ventas Fantasma (SKUs sin Inventario)")
        
        phantom = df_filtered[df_filtered['SKU_Fantasma'] == True]
        phantom_rev = phantom['Precio_Venta_Final'].sum()
        total_rev = df_filtered['Precio_Venta_Final'].sum()
        phantom_pct = (phantom_rev / total_rev * 100) if total_rev > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Revenue Fantasma", f"${phantom_rev:,.0f}")
        with col2:
            st.metric("% del Total", f"{phantom_pct:.2f}%")
        with col3:
            st.metric("Ventas Fantasma", f"{len(phantom):,}")
        
        if len(phantom) > 0:
            # Por ciudad
            by_city_phantom = phantom.groupby('Ciudad_Destino')['Precio_Venta_Final'].sum().sort_values(ascending=False)
            
            fig3 = px.bar(
                x=by_city_phantom.index,
                y=by_city_phantom.values,
                title='Revenue Fantasma por Ciudad',
                labels={'x': 'Ciudad', 'y': 'Revenue (USD)'}
            )
            st.plotly_chart(fig3, use_container_width=True)
    
    
    # ===== TAB 3: CLIENTE =====
    with tab3:
        st.markdown("## 👥 Análisis del Cliente")
        
        # Pregunta 4: Paradoja de Fidelidad
        st.markdown("### 🤔 4. Paradoja de Fidelidad (Alto Stock + Bajo NPS)")
        
        df_customer = df_filtered[df_filtered['Satisfaccion_NPS'].notna()]
        
        if len(df_customer) > 0:
            by_cat = df_customer.groupby('Categoria').agg({
                'Stock_Actual': 'mean',
                'Satisfaccion_NPS': 'mean',
                'Rating_Producto': 'mean',
                'Transaccion_ID': 'count'
            }).reset_index()
            by_cat.columns = ['Categoria', 'Stock_Prom', 'NPS_Prom', 'Rating_Prom', 'Transacciones']
            
            # Identificar paradoja
            median_stock = by_cat['Stock_Prom'].median()
            median_nps = by_cat['NPS_Prom'].median()
            
            by_cat['Paradoja'] = (by_cat['Stock_Prom'] > median_stock) & (by_cat['NPS_Prom'] < median_nps)
            
            fig4 = px.scatter(
                by_cat,
                x='Stock_Prom',
                y='NPS_Prom',
                size='Transacciones',
                color='Paradoja',
                text='Categoria',
                title='Stock vs NPS por Categoría',
                labels={'Stock_Prom': 'Stock Promedio', 'NPS_Prom': 'NPS Promedio'},
                color_discrete_map={True: 'red', False: 'blue'}
            )
            fig4.add_hline(y=median_nps, line_dash="dash", annotation_text="Mediana NPS")
            fig4.add_vline(x=median_stock, line_dash="dash", annotation_text="Mediana Stock")
            st.plotly_chart(fig4, use_container_width=True)
            
            paradox = by_cat[by_cat['Paradoja'] == True]
            if len(paradox) > 0:
                st.warning("⚠️ Categorías con Paradoja detectada:")
                st.dataframe(paradox[['Categoria', 'Stock_Prom', 'NPS_Prom', 'Rating_Prom']], 
                           use_container_width=True)
        
        st.markdown("---")
        
        # Pregunta 5: Riesgo Operativo
        st.markdown("### ⚠️ 5. Riesgo Operativo (Días sin Revisión vs Tickets)")
        
        df_risk = df_filtered[df_filtered['Ticket_Binary'].notna()]
        
        if len(df_risk) > 0:
            by_bodega = df_risk.groupby('Bodega_Origen').agg({
                'Dias_Sin_Revision': 'mean',
                'Ticket_Binary': 'mean',
                'Satisfaccion_NPS': 'mean',
                'Transaccion_ID': 'count'
            }).reset_index()
            by_bodega.columns = ['Bodega', 'Dias_Sin_Rev', 'Tasa_Tickets', 'NPS_Prom', 'Transacciones']
            by_bodega['Tasa_Tickets_Pct'] = by_bodega['Tasa_Tickets'] * 100
            
            fig5 = px.scatter(
                by_bodega,
                x='Dias_Sin_Rev',
                y='Tasa_Tickets_Pct',
                size='Transacciones',
                text='Bodega',
                title='Días sin Revisión vs Tasa de Tickets por Bodega',
                labels={'Dias_Sin_Rev': 'Días sin Revisión', 'Tasa_Tickets_Pct': 'Tasa de Tickets (%)'}
            )
            st.plotly_chart(fig5, use_container_width=True)
            
            # Bodegas de alto riesgo
            p75_days = by_bodega['Dias_Sin_Rev'].quantile(0.75)
            p75_tickets = by_bodega['Tasa_Tickets_Pct'].quantile(0.75)
            
            high_risk = by_bodega[
                (by_bodega['Dias_Sin_Rev'] > p75_days) & 
                (by_bodega['Tasa_Tickets_Pct'] > p75_tickets)
            ]
            
            if len(high_risk) > 0:
                st.error("🚨 Bodegas de Alto Riesgo:")
                st.dataframe(high_risk, use_container_width=True)
    
    
    # ===== TAB 4: IA INSIGHTS =====
    with tab4:
        st.markdown("## 🤖 Insights con IA (Groq + Llama-3)")
        
        if not groq_api_key:
            st.warning("⚠️ Por favor ingresa tu API Key de Groq en la barra lateral")
        else:
            st.markdown("### 📊 Resumen de Datos Filtrados")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_rev = df_filtered['Precio_Venta_Final'].sum()
                st.metric("Ingresos", f"${total_rev:,.0f}")
                
                total_margin = df_filtered['Margen_USD'].sum()
                st.metric("Margen Total", f"${total_margin:,.0f}")
            
            with col2:
                avg_nps = df_filtered['Satisfaccion_NPS'].mean() if df_filtered['Satisfaccion_NPS'].notna().any() else 0
                st.metric("NPS Promedio", f"{avg_nps:.1f}")
                
                avg_delivery = df_filtered['Tiempo_Entrega'].mean()
                st.metric("Tiempo Entrega", f"{avg_delivery:.1f} días")
            
            with col3:
                phantom_count = (df_filtered['SKU_Fantasma'] == True).sum()
                st.metric("Ventas Fantasma", f"{phantom_count:,}")
                
                ticket_rate = df_filtered['Ticket_Binary'].mean() * 100 if 'Ticket_Binary' in df_filtered.columns else 0
                st.metric("Tasa Tickets", f"{ticket_rate:.1f}%")
            
            st.markdown("---")
            
            if st.button("🚀 Generar Conclusiones con IA", type="primary"):
                
                # Preparar prompt
                prompt = f"""Eres un consultor senior de analytics para TechLogistics S.A.

Analiza estos datos filtrados y genera exactamente 3 párrafos de conclusiones:

DATOS:
- Ingresos totales: ${total_rev:,.0f} USD
- Margen total: ${total_margin:,.0f} USD
- NPS promedio: {avg_nps:.1f}
- Tiempo de entrega promedio: {avg_delivery:.1f} días
- Ventas fantasma: {phantom_count} transacciones
- Tasa de tickets de soporte: {ticket_rate:.1f}%
- Total de transacciones: {len(df_filtered):,}

PÁRRAFO 1 - DIAGNÓSTICO: Identifica el problema más crítico
PÁRRAFO 2 - RECOMENDACIÓN TÁCTICA: 2-3 acciones inmediatas (30 días)
PÁRRAFO 3 - ESTRATEGIA: Cambios estructurales de largo plazo

Escribe de forma ejecutiva y directa, sin bullets."""

                with st.spinner("Consultando a Llama-3..."):
                    conclusion = call_groq_api(prompt, groq_api_key)
                
                st.markdown("### 💡 Conclusiones Estratégicas")
                st.markdown(conclusion)

else:
    # Pantalla inicial
    st.markdown("## 👋 Bienvenido")
    
    st.markdown("""
    Este es el **Sistema de Soporte a la Decisión** para TechLogistics S.A.
    
    ### 📋 Instrucciones:
    
    1. **Configura tu API Key de Groq** en la barra lateral
    2. **Carga los 3 archivos CSV**:
       - inventario_central_v2.csv
       - transacciones_logistica_v2.csv
       - feedback_clientes_v2.csv
    3. **Presiona "Procesar Datos"**
    4. **Explora las pestañas de análisis**
    
    ### ✅ Checklist del Validation Guide:
    
    - ☑️ Barra lateral estructurada
    - ☑️ Módulo de transparencia (Health Score)
    - ☑️ Visualización con st.tabs
    - ☑️ Integración con Groq AI
    - ☑️ Filtros de categoría y bodega
    - ☑️ Botón de refrescar análisis
    """)
    
    st.info("👈 Comienza cargando los datos en la barra lateral")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #888;'>
    <strong>Challenge 02</strong> | Fundamentos en Ciencia de Datos | 
    Universidad EAFIT | Prof. Jorge Iván Padilla-Buriticá
</div>
""", unsafe_allow_html=True)
