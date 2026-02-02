from groq import Groq

def generar_insights_ia(df_filtrado, pregunta, api_key):

    if not api_key:
        return "❌ No se proporcionó una API Key válida."

    client = Groq(api_key=api_key)

    resumen = {
        "filas": len(df_filtrado),
        "ingresos": round(df_filtrado["Ingreso"].sum(), 2),
        "margen": round(df_filtrado["Margen_Utilidad"].sum(), 2),
        "riesgo_promedio": round(
            (df_filtrado["Ticket_Soporte_Abierto"] == "Sí").mean(), 2
        )
    }

    prompt = f"""
    Eres un analista senior de logística y negocio.

    Con base en el siguiente resumen de datos filtrados:
    {resumen}

    Responde de forma clara y accionable a la siguiente pregunta:
    {pregunta}

    Da insights ejecutivos, no técnicos.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
