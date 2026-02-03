def generar_insights_ia(df, api_key):
    if df.empty:
        return "⚠️ No hay datos suficientes..."

    client = Groq(api_key=api_key)

    # Enriquecemos el resumen con métricas de contexto para el análisis
    resumen = {
        "filas_analizadas": int(len(df)),
        "ingresos_totales_usd": safe_number(df["Ingreso"].sum()),
        "margen_total_usd": safe_number(df["Margen_Utilidad"].sum()),
        "margen_pct": safe_number(
            (df["Margen_Utilidad"].sum() / df["Ingreso"].sum()) * 100
            if df["Ingreso"].sum() > 0 else 0
        ),
        "tiempo_entrega_promedio_dias": safe_number(df["Tiempo_Entrega_Limpio"].mean()),
        "riesgo_tickets_pct": safe_number((df["Ticket_Soporte_Abierto"] == "Sí").mean() * 100),
        # Añadimos métricas de dispersión o extremos para que la IA vea "el problema"
        "peor_tiempo_entrega": safe_number(df["Tiempo_Entrega_Limpio"].max()),
        "ingreso_promedio_por_operacion": safe_number(df["Ingreso"].mean())
    }

    # PROMPT ESTRATÉGICO
    system_prompt = (
        "Eres un Senior Business Strategy & Data Scientist con 15 años de experiencia. "
        "Tu enfoque no es descriptivo (decir qué pasó), sino diagnóstico (por qué pasó) "
        "y prescriptivo (qué debemos hacer). Tienes un tono ejecutivo, directo y crítico."
    )

    user_prompt = f"""
Analiza los siguientes KPIs operativos y financieros:
{resumen}

Tu objetivo es entregar un informe ejecutivo de alto nivel que contenga:

1. **Diagnóstico de la Situación:** Identifica el problema oculto detrás de estos números. ¿Hay una fuga de margen? ¿Un problema de escalabilidad? ¿La eficiencia operativa está comprometiendo la satisfacción del cliente?
2. **Análisis de Impacto:** Explica cómo el estado actual afecta la rentabilidad a largo plazo.
3. **Plan de Acción Estratégico:** Propone 3 pasos concretos para mitigar los riesgos detectados.

REGLAS:
- No repitas los datos crudos del resumen.
- Usa terminología de negocios (Churn, ROI, Eficiencia Operativa, LTV).
- Sé incisivo: si los datos muestran una ineficiencia, señálala claramente.
- Formato: Usa Markdown con negritas para enfatizar puntos clave.
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3, # Bajamos la temperatura para mayor consistencia analítica
            max_tokens=600   # Aumentamos para un análisis más exhaustivo
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error al generar insights: {e}"
