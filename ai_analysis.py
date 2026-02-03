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
           model="llama-3.1-8b-instant"

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
