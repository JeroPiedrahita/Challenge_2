# 📦 EDA Operacional & DSS – TechLogistics S.A.S.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://challenge2.streamlit.app/)

Este proyecto consiste en el desarrollo de un **Sistema de Soporte a la Decisión (DSS)** interactivo diseñado para **TechLogistics S.A.S.**, una empresa de retail tecnológico que enfrenta una erosión en su margen de beneficios y problemas de lealtad de clientes debido a la "invisibilidad operativa".

La solución integra auditoría de calidad de datos, limpieza avanzada, análisis visual y recomendaciones estratégicas potenciadas por **IA Generativa (Llama-3.1-8b)**.

---

## 🔍 Descripción del Problema
TechLogistics opera con tres sistemas principales (Inventarios, Logística y Feedback) que presentan graves inconsistencias técnicas:
* **Inconsistencias de Tipo:** Fechas y *lead times* mezclados en el maestro de productos.
* **Integridad Referencial:** Miles de ventas de SKUs que no figuran en el inventario oficial ("Venta Invisible").
* **Datos Atípicos y Ruido:** Costos desde \$0.01 hasta \$850k, edades de clientes imposibles (195 años) y registros duplicados intencionales.

---

## 🛠️ Arquitectura del Proyecto
El repositorio sigue una estructura modular para garantizar la escalabilidad y buenas prácticas de programación (PEP8):

* `app.py`: Interfaz principal en **Streamlit**. Gestiona el estado de la sesión, los filtros dinámicos (fechas, bodegas, canales) y la visualización de KPIs.
* `data_processing.py`: Motor de limpieza. Realiza normalización de texto (Unicode), imputación de costos por mediana y gestión de valores atípicos mediante técnicas de *clipping* y filtrado estadístico.
* `ai_analysis.py`: Módulo de integración con la API de **Groq**. Procesa los datos filtrados para generar diagnósticos ejecutivos en tiempo real.
* `requirements.txt`: Dependencias del entorno (Pandas, Plotly, Groq, etc.).

---

## ⚙️ Pipeline de Trabajo
1. **Auditoría (Health Score):** Se calcula un puntaje de salud de los datos antes y después del procesamiento, reportando porcentajes de nulidad, duplicados y magnitud de outliers.
2. **Integración (Single Source of Truth):** Realiza un *Merge/Join* estratégico para unificar los tres datasets, gestionando el dilema del "SKU Fantasma".
3. **Feature Engineering:** Creación de nuevas variables como *Margen de Utilidad*, *Brecha de Entrega vs Prometido* y *Tasa de Tickets de Soporte*.

---

## 📊 Preguntas Estratégicas Resueltas
El dashboard permite responder con evidencia visual y estadística a los interrogantes de la Alta Gerencia:
1. **Rentabilidad:** Localización de SKUs con margen negativo y análisis de fallas de precios.
2. **Logística:** Correlación entre tiempos de entrega y bajo NPS para identificar zonas críticas.
3. **Impacto Financiero:** Cuantificación en USD de las ventas sin control de inventario.
4. **Paradoja de Fidelidad:** Diagnóstico de categorías con alto stock pero sentimiento negativo del cliente.
5. **Riesgo Operativo:** Relación entre la última revisión de stock y la tasa de tickets de soporte.

---

## 🤖 Uso de Inteligencia Artificial
La aplicación integra el modelo `llama-3.1-8b-instant` a través de **Groq**.

* **Entrada:** Resumen de KPIs operativos (Ingresos, Márgenes, Tasa de Tickets).
* **Salida:** Un diagnóstico incisivo, análisis de impacto y un plan de acción estratégico de 3 pasos con terminología de negocios (*Churn, ROI, Eficiencia*).

> **Nota:** Se requiere una API Key de Groq para habilitar esta función en la pestaña de "Insights IA".

---

## 🚀 Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto localmente:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/JeroPiedrahita/Challenge_2.git](https://github.com/JeroPiedrahita/Challenge_2.git)
   cd Challenge_2
2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt

3. **Ejecutar la App:**

   ```bash
   streamlit run app.py
---
## 🤖 **Uso de Inteligencia Artificial**
La aplicación integra el modelo llama-3.1-8b-instant a través de Groq.

*Entrada: Resumen de KPIs operativos (Ingresos, Márgenes, Tasa de Tickets).

*Salida: Un diagnóstico incisivo, análisis de impacto y un plan de acción estratégico de 3 pasos con terminología de negocios (Churn, ROI, Eficiencia).

Nota: Se requiere una API Key de Groq para habilitar esta función en la pestaña de "Insights IA".

---
## 🎓 **Créditos**
Estudiante: Marcela Londoño Leon-Jerónimo Piedrahita Franco

Curso: Fundamentos en Ciencia de Datos (Maestría en Ingeniería)

Institución: Universidad EAFIT

Periodo: 2026-1

---
##
**Accede a la app en vivo aquí: https://challenge2.streamlit.app/**
