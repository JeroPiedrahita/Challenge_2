# 📦 EDA Operacional & DSS – TechLogistics S.A.S.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://challenge2.streamlit.app/)

[cite_start]Este proyecto consiste en el desarrollo de un **Sistema de Soporte a la Decisión (DSS)** interactivo diseñado para **TechLogistics S.A.S.**, una empresa de retail tecnológico que enfrenta una erosión en su margen de beneficios y problemas de lealtad de clientes debido a la "invisibilidad operativa"[cite: 7, 8, 9]. 

[cite_start]La solución integra auditoría de calidad de datos, limpieza avanzada, análisis visual y recomendaciones estratégicas potenciadas por **IA Generativa (Llama-3.1-8b)**[cite: 31, 32].

---

## 🔍 Descripción del Problema
[cite_start]TechLogistics opera con tres sistemas principales (Inventarios, Logística y Feedback) que presentan graves inconsistencias técnicas[cite: 8, 11]:
* [cite_start]**Inconsistencias de Tipo:** Fechas y *lead times* mezclados en el maestro de productos[cite: 12].
* [cite_start]**Integridad Referencial:** Miles de ventas de SKUs que no figuran en el inventario oficial ("Venta Invisible")[cite: 13, 14, 41].
* [cite_start]**Datos Atípicos y Ruido:** Costos desde \$0.01 hasta \$850k, edades de clientes imposibles (195 años) y registros duplicados intencionales[cite: 12, 16].

---

## 🛠️ Arquitectura del Proyecto
[cite_start]El repositorio sigue una estructura modular para garantizar la escalabilidad y buenas prácticas de programación (PEP8)[cite: 55]:

* `app.py`: Interfaz principal en **Streamlit**. [cite_start]Gestiona el estado de la sesión, los filtros dinámicos (fechas, bodegas, canales) y la visualización de KPIs[cite: 49].
* `data_processing.py`: Motor de limpieza. [cite_start]Realiza normalización de texto (Unicode), imputación de costos por mediana y gestión de valores atípicos mediante técnicas de *clipping* y filtrado estadístico[cite: 19, 21, 22].
* `ai_analysis.py`: Módulo de integración con la API de **Groq**. [cite_start]Procesa los datos filtrados para generar diagnósticos ejecutivos en tiempo real[cite: 32].
* `requirements.txt`: Dependencias del entorno (Pandas, Plotly, Groq, etc.).

---

## ⚙️ Pipeline de Trabajo
1.  [cite_start]**Auditoría (Health Score):** Se calcula un puntaje de salud de los datos antes y después del procesamiento, reportando porcentajes de nulidad, duplicados y magnitud de outliers[cite: 19, 20].
2.  [cite_start]**Integración (Single Source of Truth):** Realiza un *Merge/Join* estratégico para unificar los tres datasets, gestionando el dilema del "SKU Fantasma"[cite: 27, 28].
3.  [cite_start]**Feature Engineering:** Creación de nuevas variables como *Margen de Utilidad*, *Brecha de Entrega vs Prometido* y *Tasa de Tickets de Soporte*[cite: 30].

---

## 📊 Preguntas Estratégicas Resueltas
[cite_start]El dashboard permite responder con evidencia visual y estadística a los interrogantes de la Alta Gerencia[cite: 33, 35, 36]:
1.  [cite_start]**Rentabilidad:** Localización de SKUs con margen negativo y análisis de fallas de precios[cite: 37, 38].
2.  [cite_start]**Logística:** Correlación entre tiempos de entrega y bajo NPS para identificar zonas críticas[cite: 39, 40].
3.  [cite_start]**Impacto Financiero:** Cuantificación en USD de las ventas sin control de inventario[cite: 41, 42].
4.  [cite_start]**Paradoja de Fidelidad:** Diagnóstico de categorías con alto stock pero sentimiento negativo del cliente[cite: 43, 44].
5.  [cite_start]**Riesgo Operativo:** Relación entre la última revisión de stock y la tasa de tickets de soporte[cite: 45, 46].

---

## 🚀 Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto localmente:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/JeroPiedrahita/Challenge_2.git](https://github.com/JeroPiedrahita/Challenge_2.git)
   cd Challenge_2
Instalar dependencias:
2. **Instalar dependencias:**

pip install -r requirements.txt

3. **Ejecutar la App:**


streamlit run app.py

🤖 **Uso de Inteligencia Artificial**
La aplicación integra el modelo llama-3.1-8b-instant a través de Groq.

*Entrada: Resumen de KPIs operativos (Ingresos, Márgenes, Tasa de Tickets).

*Salida: Un diagnóstico incisivo, análisis de impacto y un plan de acción estratégico de 3 pasos con terminología de negocios (Churn, ROI, Eficiencia).

Nota: Se requiere una API Key de Groq para habilitar esta función en la pestaña de "Insights IA".

🎓 **Créditos**
Estudiante: Marcela Londoño Leon-Jerónimo Piedrahita Franco

Curso: Fundamentos en Ciencia de Datos (Maestría en Ingeniería)

Institución: Universidad EAFIT

Periodo: 2026-1

**Accede a la app en vivo aquí: https://challenge2.streamlit.app/**
