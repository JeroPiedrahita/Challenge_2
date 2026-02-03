from groq import Groq

def generar_insights_ia(df, api_key):

    client = Groq(api_key=api_key)

    # --- Resumen ejecutivo NUMÉRICO ---
    resumen = {
        "filas_analizadas": int(len(df)),
        "ingresos_totales_usd": round(df["Ingreso"].sum(), 2),
        "margen_total_usd": round(df["Margen_Utilidad"].sum(), 2),
        "margen_pct": round(
            (df["Margen_Utilidad"].sum() / df["Ingreso"].sum()) * 100
            if df["Ingreso"].sum() > 0 else 0,
            2
        ),
        "tiempo_entrega_promedio": round(df["Tiempo_Entrega_Limpio"].mean(), 2),
        "riesgo_tickets_pct": round(
            (df["Ticket_Soporte_Abierto"] == "Sí").mean() * 100,
            2
        )
    }

    # --- PROMPT CONTROLADO ---
    prompt = f"""
Eres un analista senior de operaciones y logística.

A partir del siguiente resumen de datos operativos,
genera EXACTAMENTE 3 insights claros, accionables y
orientados a toma de decisiones gerenciales.

No repitas números sin analizarlos.
No des explicaciones técnicas.
Usa lenguaje ejecutivo.

Resumen:
{resumen}
"""

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": "Eres un experto en análisis de negocio."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=400
    )

    return response.choices[0].message.content
