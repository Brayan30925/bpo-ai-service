
import os
import json
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


# Localizar el archivo .env en la raíz del proyecto
RUTA_ENV = Path(__file__).resolve().parents[2] / ".env"

load_dotenv(dotenv_path=RUTA_ENV)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")


def obtener_cliente_groq():
    """
    Crea el cliente de conexión con Groq.
    """
    if not GROQ_API_KEY:
        raise ValueError(
            "No se encontró GROQ_API_KEY en las variables de entorno"
        )

    return Groq(api_key=GROQ_API_KEY)


def clasificar_con_ia(descripcion: str, categorias: list) -> dict:
    """
    Utiliza IA para identificar la categoría de una solicitud
    según las categorías configuradas para la empresa.
    """

    cliente = obtener_cliente_groq()

    categorias_disponibles = [
        categoria["nombre"]
        for categoria in categorias
    ]

    mensaje = f"""
Analiza la siguiente solicitud de servicio.

SOLICITUD:
{descripcion}

CATEGORÍAS DISPONIBLES:
{json.dumps(categorias_disponibles, ensure_ascii=False)}

Selecciona la categoría que mejor represente la solicitud.

REGLAS:
1. Solo puedes seleccionar una categoría de la lista.
2. No inventes categorías.
3. Si ninguna categoría corresponde, utiliza null.
4. Justifica brevemente tu decisión utilizando información
   presente en la solicitud.
5. No inventes información.

Responde exclusivamente con un objeto JSON con esta estructura:

{{
    "categoria": "Nombre de la categoría o null",
    "justificacion": "Explicación de la clasificación",
    "evidencia": ["frase relevante de la solicitud"]
}}
"""

    respuesta = cliente.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Eres un asistente especializado en clasificación "
                    "de solicitudes empresariales BPO. "
                    "Debes responder exclusivamente en formato JSON."
                )
            },
            {
                "role": "user",
                "content": mensaje
            }
        ],
        response_format={"type": "json_object"},
        temperature=0.1
    )

    contenido = respuesta.choices[0].message.content

    return json.loads(contenido)
