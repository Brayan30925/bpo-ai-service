
import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.validador import validar_solicitud
from app.services.clasificador import clasificar_solicitud
from app.services.prioridad import asignar_prioridad
from app.services.configuracion import obtener_configuracion
from app.services.decision_service import determinar_siguiente_paso

from app.services.integracion_service import (
    crear_caso_externo,
    registrar_error_integracion,
    marcar_error_solucionado
)


logger = logging.getLogger(__name__)


app = FastAPI(
    title="BPO AI Service",
    description="Servicio de automatización y clasificación de solicitudes BPO",
    version="1.0.0"
)


class SolicitudEntrada(BaseModel):
    solicitud_id: str = Field(min_length=1)
    empresa: str = Field(min_length=1)
    descripcion: str = Field(min_length=1)
    datos_adicionales: Optional[dict] = None


class ValidacionEntrada(BaseModel):
    descripcion: str = Field(min_length=1)


@app.get("/")
def inicio():
    return {
        "mensaje": "BPO AI Service funcionando correctamente",
        "estado": "activo"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/solicitudes")
def recibir_solicitud(solicitud: SolicitudEntrada):

    # 1. Obtener configuración de la empresa
    configuracion = obtener_configuracion(solicitud.empresa)

    if configuracion is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no parametrizada"
        )

    # 2. Validar información mínima
    validacion = validar_solicitud(solicitud.descripcion)

    if not validacion["valida"]:

        decision = determinar_siguiente_paso(
            False,
            {},
            configuracion
        )

        return {
            "compania": solicitud.empresa,
            "solicitud_id": solicitud.solicitud_id,
            "solicitud_valida": False,
            **decision,
            "faltantes": validacion["faltantes"]
        }

    # 3. Clasificar solicitud
    clasificacion = clasificar_solicitud(
        solicitud.empresa,
        solicitud.descripcion
    )

    # 4. Asignar prioridad según la estrategia de la empresa
    prioridad = asignar_prioridad(
        empresa=solicitud.empresa,
        descripcion=solicitud.descripcion,
        datos_adicionales=solicitud.datos_adicionales,
        tipo_solicitud=clasificacion.get("categoria")
    )

    # 5. Determinar el siguiente paso
    decision = determinar_siguiente_paso(
        True,
        clasificacion,
        configuracion
    )

    # 6. Si no se pudo determinar la prioridad,
    # enviar a revisión manual y no crear caso externo.
    if not prioridad.get("asignada"):

        decision = {
            "proximo_paso": "REVISION_MANUAL",
            "estado": "pendiente_revision",
            "justificacion": (
                "No fue posible determinar la prioridad. "
                + prioridad.get(
                    "justificacion",
                    "Se requiere revisión manual."
                )
            )
        }

    integracion = None

    # 7. Crear caso externo solamente cuando
    # la prioridad y la decisión sean correctas.
    if (
        decision["proximo_paso"] == "GESTION_EXTERNA"
        and prioridad.get("asignada")
    ):

        try:

            integracion = crear_caso_externo(
                empresa=solicitud.empresa,
                solicitud_id=solicitud.solicitud_id,
                descripcion=solicitud.descripcion,
                prioridad=prioridad["prioridad"],
                categoria=clasificacion["categoria"]
            )

            if integracion.get("conflicto_detectado"):

                decision["proximo_paso"] = "REVISION_MANUAL"
                decision["estado"] = "pendiente_revision"
                decision["justificacion"] = (
                    "La solicitud ya existe con información diferente. "
                    "Se requiere revisión manual."
                )

            elif integracion.get("integracion_exitosa"):

                # La creación del caso ya fue exitosa.
                # Un fallo al actualizar el registro de errores
                # no debe marcar la integración como fallida.
                try:
                    marcar_error_solucionado(
                        empresa=solicitud.empresa,
                        solicitud_id=solicitud.solicitud_id
                    )

                except Exception:
                    logger.exception(
                        "No fue posible actualizar el registro de error "
                        "para solicitud_id=%s",
                        solicitud.solicitud_id
                    )

        except Exception as error:

            logger.exception(
                "Error de integración para solicitud_id=%s",
                solicitud.solicitud_id
            )

            try:
                registro_error = registrar_error_integracion(
                    empresa=solicitud.empresa,
                    solicitud_id=solicitud.solicitud_id,
                    mensaje_error=str(error)
                )

            except Exception:

                logger.exception(
                    "No fue posible registrar el error de integración"
                )

                registro_error = {
                    "error_registrado": False,
                    "estado_reintento": "PENDIENTE",
                    "numero_intentos": 0
                }

            integracion = {
                "integracion_exitosa": False,
                "caso_duplicado": False,
                "conflicto_detectado": False,
                "estado_integracion": "error",
                "requiere_reintento": True,
                **registro_error,
                "mensaje": (
                    "No fue posible completar la integración. "
                    "La solicitud requiere revisión o reintento."
                )
            }

    # 8. Construir respuesta
    return {
        "compania": solicitud.empresa,
        "solicitud_id": solicitud.solicitud_id,
        "solicitud_valida": True,
        "solicitud_tipo": clasificacion.get("categoria"),
        "clasificacion": clasificacion,
        "solicitud_prioridad": prioridad.get("prioridad"),
        "prioridad": prioridad,
        **decision,
        "integracion_externa": integracion
    }


@app.post("/validar")
def validar(solicitud: ValidacionEntrada):
    return validar_solicitud(solicitud.descripcion)


@app.post("/clasificar")
def clasificar(solicitud: SolicitudEntrada):
    return clasificar_solicitud(
        solicitud.empresa,
        solicitud.descripcion
    )


@app.post("/prioridad")
def calcular_prioridad(solicitud: SolicitudEntrada):

    configuracion = obtener_configuracion(solicitud.empresa)

    if configuracion is None:
        raise HTTPException(
            status_code=404,
            detail="Empresa no parametrizada"
        )

    clasificacion = clasificar_solicitud(
        solicitud.empresa,
        solicitud.descripcion
    )

    return asignar_prioridad(
        empresa=solicitud.empresa,
        descripcion=solicitud.descripcion,
        datos_adicionales=solicitud.datos_adicionales,
        tipo_solicitud=clasificacion.get("categoria")
    )
