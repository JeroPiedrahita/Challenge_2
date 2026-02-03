from groq import Groq
import math


def safe_number(x):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return 0
    return round(float(x), 2)


def generar_insights_ia(df, api_key):

    if df.empty:
        return (
            "⚠️ No hay datos suficientes con los filtros actuales.\n\n"
            "Ajusta el rango de fechas o los filtros para generar insights."
        )

    client = Groq(api_key=api_key)

    resumen = {
        "filas_analizadas": int(len(df)),
        "ingresos_totales_usd": safe_number(df["Ingreso"].sum()),
        "margen_total_usd": safe_number(df["Margen_Utilidad"].sum()),
        "margen_pct": safe_number(
            (df["Margen_Utilidad"].sum() / df["Ingreso"].sum()) * 100
            if df["Ingreso"].sum() > 0 else 0
        ),
        "tiempo_entrega_promedio_dias": safe_number(
            df["Tiempo_Entrega_Limpio"].mean()
        ),
        "riesgo_tickets_pct": safe_number(
            (df["Ticket_Soporte_Abierto"] == "Sí").mean() * 100
        )
    }

    prompt = f"""
Eres un analista senior de operaciones y logística.

A partir del siguiente resumen operativo,
genera EXACTAMENTE 3 insights claros,
accionables y orientados a toma de decisiones
para un gerente.

No repitas los números.
No uses lenguaje técnico.
No menciones que eres una IA.

Resumen:
{resumen}
"""

    try:
        response = client.chat.completions.create(
            model="Llama3"
,
            messages=[
                {"role": "system", "content": "Eres un experto en análisis de negocio."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=350
        )

        return response.choices[0].message.content

    except Exception as e:
        return (
            "❌ Error al generar insights con IA.\n\n"
            f"Detalle técnico: {e}"
        )
