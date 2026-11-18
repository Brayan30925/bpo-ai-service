
from app.services.configuracion import (
    obtener_configuracion,
    normalizar_texto
)

from app.services.ai_service import clasificar_con_ia


def clasificar_por_reglas(descripcion: str, categorias: list) -> dict:
    """
    Clasificación alternativa mediante palabras clave.
    """

    texto = normalizar_texto(descripcion)

    mejor_categoria = None
    mejores_coincidencias = []

    for categoria in categorias:
        coincidencias = []

        for palabra in categoria["palabras_clave"]:
            palabra_normalizada = normalizar_texto(palabra)

            if palabra_normalizada in texto:
                coincidencias.append(palabra)

        if len(coincidencias) > len(mejores_coincidencias):
            mejor_categoria = categoria["nombre"]
            mejores_coincidencias = coincidencias

    if mejor_categoria is None:
        return {
            "clasificada": False,
            "categoria": None,
            "justificacion": "No se identificó una categoría",
            "coincidencias": [],
            "metodo": "REGLAS"
        }

    return {
        "clasificada": True,
        "categoria": mejor_categoria,
        "justificacion": "Categoría identificada mediante palabras clave",
        "coincidencias": mejores_coincidencias,
        "metodo": "REGLAS"
    }


def clasificar_solicitud(empresa: str, descripcion: str) -> dict:
    """
    Clasifica una solicitud utilizando IA con alternativa por reglas.
    """

    configuracion = obtener_configuracion(empresa)

    if configuracion is None:
        return {
            "clasificada": False,
            "categoria": None,
            "justificacion": "Empresa no parametrizada",
            "coincidencias": [],
            "metodo": "NINGUNO"
        }

    categorias = configuracion["categorias"]

    try:
        resultado_ia = clasificar_con_ia(
            descripcion,
            categorias
        )

        categoria_ia = resultado_ia.get("categoria")

        categorias_validas = [
            categoria["nombre"]
            for categoria in categorias
        ]

        if categoria_ia not in categorias_validas:
            raise ValueError("La IA devolvió una categoría no permitida")

        return {
            "clasificada": True,
            "categoria": categoria_ia,
            "justificacion": resultado_ia.get("justificacion"),
            "coincidencias": resultado_ia.get("evidencia", []),
            "metodo": "IA_GROQ"
        }

    except Exception:
        resultado = clasificar_por_reglas(
            descripcion,
            categorias
        )

        resultado["justificacion"] = (
            "Se utilizó clasificación alternativa por reglas "
            "porque el servicio de IA no estuvo disponible o "
            "su respuesta no fue válida. "
            + resultado["justificacion"]
        )

        return resultado
