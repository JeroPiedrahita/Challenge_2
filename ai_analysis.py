from groq import Groq
import pandas as pd
client = Groq(
    api_key=st.secrets["GROQ_API_KEY"]
)

def generar_insights_ia(df_filtrado, pregunta_negocio):
    """
    Genera insights usando Llama-3 basados SOLO en el dataframe filtrado
    """

    # 1. Resumen numérico que sí entiende la IA
    resumen = df_filtrado.describe(include="all").to_string()

    # 2. Prompt controlado (esto es CLAVE)
    prompt = f"""
Eres un analista senior de datos.
Analiza la siguiente información y responde de forma clara, ejecutiva y accionable.

Pregunta de negocio:
{pregunta_negocio}

Resumen estadístico de los datos:
{resumen}

Entrega:
- 3 a 5 insights clave
- Riesgos detectados
- Oportunidades de mejora
- Recomendaciones accionables
"""

    client = Groq(api_key="TU_API_KEY_AQUI")

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content
