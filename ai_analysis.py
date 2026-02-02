from groq import Groq

def generar_insights_ia(df_filtrado, api_key):

    if not api_key:
        return "❌ No se proporcionó una API Key válida."

    client = Groq(api_key=api_key)

    resumen = {
        "ventas": len(df_filtrado),
        "ingresos_totales": round(df_filtrado["Ingreso"].sum(), 2),
        "margen_total": round(df_filtrado["Margen_Utilidad"].sum(), 2),
        "margen_promedio": round(df_filtrado["Margen_Utilidad"].mean(), 2),
        "tiempo_entrega_promedio": round(df_filtrado["Tiempo_Entrega_Limpio"].mean(), 2),
        "riesgo_operativo": round(
            (df_filtrado["Ticket_Soporte_Abierto"] == "Sí").mean() * 100, 1
        )
    }

    prompt = f"""
    Actúa como un **analista senior de logística y negocio**.

    A partir del siguiente resumen de datos operativos filtrados:
    {resumen}

    Genera un **informe ejecutivo** con:

    1. Principales hallazgos operativos
    2. Identificación de riesgos logísticos y financieros
    3. Impacto del desempeño logístico sobre el margen
    4. Recomendaciones claras y accionables para la gerencia

    Usa un lenguaje claro, profesional y orientado a decisiones.
    No menciones modelos, IA ni aspectos técnicos.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
