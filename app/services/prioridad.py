
from app.services.configuracion import (
    obtener_configuracion,
    normalizar_texto
)

from app.services.cliente_prioridad_service import (
    consultar_prioridad_cliente
)


ORDEN_PRIORIDAD = {
    "Alta": 3,
    "Media": 2,
    "Baja": 1
}


def asignar_prioridad(
    empresa: str,
    descripcion: str,
    datos_adicionales: dict | None = None,
    tipo_solicitud: str | None = None
) -> dict:

    configuracion = obtener_configuracion(empresa)

    if configuracion is None:
        return {
            "asignada": False,
            "prioridad": None,
            "justificacion": "Empresa no parametrizada"
        }

    configuracion_prioridad = configuracion.get("prioridades")

    if not configuracion_prioridad:
        return {
            "asignada": False,
            "prioridad": None,
            "justificacion": "Empresa sin reglas de prioridad"
        }

    tipo_estrategia = configuracion_prioridad.get("tipo")

    # Estrategia 1: reglas locales
    if tipo_estrategia == "reglas_provisionales":
        return asignar_prioridad_por_reglas(
            descripcion,
            configuracion_prioridad
        )

    # Estrategia 2: microservicio del cliente
    if tipo_estrategia == "microservicio":

        datos = datos_adicionales or {}

        return consultar_prioridad_cliente(
            tipo_documento=datos.get("tipo_documento"),
            numero_documento_cliente=datos.get(
                "numero_documento_cliente"
            ),
            tipo_solicitud=tipo_solicitud
        )

    return {
        "asignada": False,
        "prioridad": None,
        "justificacion": (
            f"Estrategia de prioridad no reconocida: "
            f"{tipo_estrategia}"
        )
    }


def asignar_prioridad_por_reglas(
    descripcion: str,
    configuracion_prioridad: dict
) -> dict:

    texto = normalizar_texto(descripcion)

    coincidencias_prioridad = {}

    for regla in configuracion_prioridad.get("reglas", []):

        prioridad = regla["prioridad"]
        coincidencias = []

        for palabra in regla["palabras_clave"]:

            palabra_normalizada = normalizar_texto(palabra)

            if palabra_normalizada in texto:
                coincidencias.append(palabra)

        if coincidencias:
            coincidencias_prioridad[prioridad] = coincidencias

    if coincidencias_prioridad:

        prioridad_seleccionada = max(
            coincidencias_prioridad,
            key=lambda prioridad: ORDEN_PRIORIDAD.get(
                prioridad,
                0
            )
        )

        coincidencias = coincidencias_prioridad[
            prioridad_seleccionada
        ]

        justificacion = (
            f"Se asignó prioridad {prioridad_seleccionada} "
            f"por las siguientes coincidencias: "
            f"{', '.join(coincidencias)}."
        )

    else:

        prioridad_seleccionada = (
            configuracion_prioridad.get(
                "prioridad_por_defecto"
            )
        )

        coincidencias = []

        justificacion = (
            "No se encontraron indicadores específicos. "
            f"Se asignó la prioridad por defecto: "
            f"{prioridad_seleccionada}."
        )

    if prioridad_seleccionada not in ORDEN_PRIORIDAD:
        return {
            "asignada": False,
            "prioridad": None,
            "justificacion": (
                "La prioridad configurada no es válida."
            ),
            "tipo_regla": "reglas_provisionales"
        }

    return {
        "asignada": True,
        "prioridad": prioridad_seleccionada,
        "justificacion": justificacion,
        "coincidencias": coincidencias,
        "tipo_regla": "reglas_provisionales"
    }
