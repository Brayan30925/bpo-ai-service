
def determinar_siguiente_paso(
    solicitud_valida: bool,
    clasificacion: dict,
    configuracion: dict
) -> dict:

    # 1. Información insuficiente
    if not solicitud_valida:
        return {
            "proximo_paso": "CIERRE_POR_INFORMACION_INSUFICIENTE",
            "estado": "cerrado",
            "justificacion": "Información incompleta o faltante"
        }

    # 2. Verificar clasificación
    if not clasificacion.get("clasificada"):
        return {
            "proximo_paso": "REVISION_MANUAL",
            "estado": "pendiente_revision",
            "justificacion": "No fue posible identificar una categoría"
        }

    # 3. Obtener el nombre de la categoría
    categoria = clasificacion.get("categoria")

    if not isinstance(categoria, str):
        return {
            "proximo_paso": "REVISION_MANUAL",
            "estado": "pendiente_revision",
            "justificacion": "Formato de categoría incorrecto"
        }

    # 4. Consultar delegaciones
    delegaciones = configuracion.get("delegaciones", {})
    delegacion = delegaciones.get(categoria)

    if not delegacion:
        return {
            "proximo_paso": "REVISION_MANUAL",
            "estado": "pendiente_revision",
            "justificacion": f"No existe delegación para {categoria}"
        }

    # 5. Determinar siguiente paso
    proximo_paso = delegacion.get("proximo_paso")

    if proximo_paso == "GESTION_EXTERNA":
        estado = "pendiente"

    elif proximo_paso == "RESPUESTA_DIRECTA":
        estado = "pendiente_respuesta"

    else:
        return {
            "proximo_paso": "REVISION_MANUAL",
            "estado": "pendiente_revision",
            "justificacion": "Delegación configurada no reconocida"
        }

    # 6. Respuesta
    return {
        "proximo_paso": proximo_paso,
        "estado": estado,
        "justificacion": (
            f"Ruta determinada según la delegación "
            f"configurada para {categoria}"
        )
    }
