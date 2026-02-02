import streamlit as st
from groq import Groq


def generar_insights_ia(df_f, pregunta):

    client = Groq(
        api_key=st.secrets["GROQ_API_KEY"]
    )

    resumen = {
        "filas": len(df_f),
        "ingresos": float(df_f["Ingreso"].sum()),
        "margen": float(df_f["Margen_Utilidad"].sum()),
        "riesgo_promedio": float(
            (df_f["Ticket_Soporte_Abierto"] == "Sí").mean()
        )
    }

    prompt = f"""
    Eres un analista senior de operaciones logísticas.

    Pregunta del usuario:
    {pregunta}

    Resumen operativo:
    {resumen}

    Genera 3 insights claros y accionables.
    """

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content
