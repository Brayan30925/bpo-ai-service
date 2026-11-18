
import json
import unicodedata
from pathlib import Path


RUTA_CONFIGURACIONES = (
    Path(__file__).resolve().parents[1]
    / "configurations"
    / "empresas"
)


def normalizar_texto(texto: str) -> str:
    """Normaliza texto eliminando mayúsculas y tildes."""

    texto = texto.lower().strip()
    texto = unicodedata.normalize("NFD", texto)

    return "".join(
        caracter
        for caracter in texto
        if unicodedata.category(caracter) != "Mn"
    )


def obtener_configuracion(empresa: str) -> dict | None:
    """Obtiene la configuración de una empresa."""

    empresa_buscada = normalizar_texto(empresa)

    if not RUTA_CONFIGURACIONES.exists():
        return None

    for archivo in RUTA_CONFIGURACIONES.glob("*.json"):

        try:
            with open(archivo, "r", encoding="utf-8") as f:
                configuracion = json.load(f)

        except (OSError, json.JSONDecodeError):
            continue

        nombre_empresa = normalizar_texto(
            configuracion.get("empresa", "")
        )

        if nombre_empresa == empresa_buscada:
            return configuracion

    return None
