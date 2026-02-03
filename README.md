📦 EDA Operacional & DSS – TechLogistics S.A.S.

Este proyecto es un Sistema de Soporte a la Decisión (DSS) interactivo desarrollado para TechLogistics S.A.S. El objetivo principal es resolver la "invisibilidad operativa" de la compañía mediante la integración y curaduría de datos provenientes de sistemas de inventario, logística y feedback de clientes.

La solución utiliza Streamlit para la interfaz visual y IA Generativa (Llama-3.1-8b) para la generación de insights estratégicos de alto nivel.

📑 Tabla de Contenido

*Descripción del Problema

*Funcionalidades Clave

*Arquitectura del Repositorio

*Instalación y Configuración

*Uso de Inteligencia Artificial

*Créditos

🔍 Descripción del Problema

TechLogistics enfrenta una erosión en sus márgenes y una caída en la lealtad del cliente. Los datos crudos presentan desafíos técnicos críticos:

Inconsistencias de Tipo: Fechas mal formateadas y tiempos de entrega mezclados.

Integridad Referencial: Ventas registradas de productos que no existen en el inventario maestro (SKUs Fantasmas).

Calidad de Datos: Valores atípicos en costos, edades de clientes inconsistentes y ruido en las métricas de satisfacción (NPS).

Este DSS transforma esos datos en tableros de control limpios y accionables.

✨ Funcionalidades Clave

Auditoría de Datos en Tiempo Real: Cálculo automático de un Health Score basado en nulidad, duplicados y outliers.

Pipeline de Limpieza Modular: Procesamiento de texto (normalización NFKD), imputación de costos por mediana de categoría y manejo de errores de fecha.

Análisis Cruzado: Exploración interactiva de la relación entre logística (tiempos de entrega) y rentabilidad (márgenes por bodega).

Dashboard de Riesgo: Visualización de tickets de soporte abiertos y su impacto en el sentimiento del cliente.

🛠️ Arquitectura del Repositorio

app.py: El corazón de la aplicación. Gestiona la interfaz, los filtros interactivos y las visualizaciones con Plotly.

data_processing.py: Contiene la lógica de limpieza y transformación de datos (Separación de responsabilidades).

ai_analysis.py: Módulo que conecta con la API de Groq para transformar KPIs crudos en informes ejecutivos.

requirements.txt: Lista de librerías necesarias (Pandas, Plotly, Groq, etc.).

🚀 Instalación y Configuración

Para ejecutar este proyecto localmente:

Clonar el repositorio:

Bash
git clone https://https://github.com/JeroPiedrahita/Challenge_2.git
cd /Challenge_2
Instalar dependencias:

Bash
pip install -r requirements.txt
Ejecutar la App:

Bash
streamlit run app.py
🤖 Uso de Inteligencia Artificial
La aplicación integra el modelo llama-3.1-8b-instant a través de Groq.

Entrada: Resumen de KPIs operativos (Ingresos, Márgenes, Tasa de Tickets).

Salida: Un diagnóstico incisivo, análisis de impacto y un plan de acción estratégico de 3 pasos con terminología de negocios (Churn, ROI, Eficiencia).

Nota: Se requiere una API Key de Groq para habilitar esta función en la pestaña de "Insights IA".

🎓 Créditos

Estudiante: Marcela Londoño Leon - Jerónimo Piedrahita Franco

Curso: Fundamentos en Ciencia de Datos (Maestría en Ingeniería)

Institución: Universidad EAFIT

Periodo: 2026-1

Accede a la app en vivo aquí: https://challenge2.streamlit.app/
