
import re


def validar_solicitud(descripcion: str) -> dict:
    """
    Verifica si una solicitud contiene información mínima:
    - Qué ocurrió.
    - Cuándo ocurrió.
    - Qué necesita el usuario.
    """

    texto = descripcion.lower()

    if not texto or len(texto.strip()) < 20:
        return {
            "valida": False,
            "justificacion": "Información incompleta o faltante",
            "faltantes": ["Descripción insuficiente"]
        }

    # Indicadores básicos de tiempo
    patrones_tiempo = [
        r"\bhoy\b", r"\bayer\b", r"\bmañana\b",
        r"\bhace\b", r"\bfecha\b", r"\bdía\b",
        r"\bsemana\b", r"\bmes\b", r"\b\d{1,2}/\d{1,2}/\d{2,4}\b"
    ]

    # Indicadores de una situación o problema
    patrones_evento = [
        r"\bproblema\b", r"\bfalla\b", r"\bdaño\b",
        r"\bocurrió\b", r"\bpasó\b", r"\bno funciona\b",
        r"\bsolicito\b", r"\bnecesito\b", r"\bme sucedió\b"
    ]

    # Indicadores de lo que necesita el usuario
    patrones_necesidad = [
        r"\bsolicito\b", r"\bnecesito\b", r"\brequiero\b",
        r"\bquiero\b", r"\bpor favor\b", r"\bque me\b"
    ]

    faltantes = []

    if not any(re.search(p, texto) for p in patrones_evento):
        faltantes.append("Qué ocurrió")

    if not any(re.search(p, texto) for p in patrones_tiempo):
        faltantes.append("Cuándo ocurrió")

    if not any(re.search(p, texto) for p in patrones_necesidad):
        faltantes.append("Qué necesita el usuario")

    if faltantes:
        return {
            "valida": False,
            "justificacion": "Información incompleta o faltante",
            "faltantes": faltantes
        }

    return {
        "valida": True,
        "justificacion": "La solicitud contiene información mínima",
        "faltantes": []
    }




