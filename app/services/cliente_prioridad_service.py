
import json
import os

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


PRIORIDADES_VALIDAS = {"Alta", "Media", "Baja"}


def consultar_prioridad_cliente(
    tipo_documento: str,
    numero_documento_cliente: str,
    tipo_solicitud: str
) -> dict:

    url = os.getenv("MENSAJERIA_PRIORIDAD_URL")

    if not url:
        return {
            "asignada": False,
            "prioridad": None,
            "justificacion": (
                "No está configurada la URL del microservicio."
            )
        }

    if not all([
        tipo_documento,
        numero_documento_cliente,
        tipo_solicitud
    ]):
        return {
            "asignada": False,
            "prioridad": None,
            "justificacion": (
                "Faltan datos obligatorios para consultar "
                "la prioridad del cliente."
            )
        }

    datos = {
        "tipo_documento": tipo_documento,
        "numero_documento_cliente": numero_documento_cliente,
        "tipo_solicitud": tipo_solicitud
    }

    try:
        contenido = json.dumps(datos).encode("utf-8")

        solicitud = Request(
            url,
            data=contenido,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urlopen(solicitud, timeout=5) as respuesta:
            resultado = json.loads(
                respuesta.read().decode("utf-8")
            )

        if not isinstance(resultado, dict):
            raise ValueError("Respuesta JSON inválida")

        prioridad = resultado.get("prioridad")
        justificacion = resultado.get("justificacion")
        perfil_cliente = resultado.get("perfil_cliente")

        if prioridad not in PRIORIDADES_VALIDAS:
            raise ValueError(
                "El servicio devolvió una prioridad inválida"
            )

        if (
            not isinstance(justificacion, str)
            or not justificacion.strip()
        ):
            raise ValueError(
                "El servicio no devolvió una justificación válida"
            )

        if (
            perfil_cliente is not None
            and (
                not isinstance(perfil_cliente, str)
                or not perfil_cliente.strip()
            )
        ):
            raise ValueError(
                "El perfil del cliente devuelto no es válido"
            )

        return {
            "asignada": True,
            "prioridad": prioridad,
            "justificacion": justificacion,
            "tipo_regla": "microservicio",
            "origen": "MENSAJERIA_DEL_VALLE",
            "perfil_cliente": perfil_cliente
        }

    except HTTPError as error:
        mensaje = (
            f"El microservicio respondió con HTTP {error.code}"
        )

    except URLError:
        mensaje = (
            "No fue posible conectar con el microservicio."
        )

    except TimeoutError:
        mensaje = (
            "El microservicio superó el tiempo de espera."
        )

    except (ValueError, json.JSONDecodeError):
        mensaje = (
            "El microservicio devolvió una respuesta inválida."
        )

    except Exception:
        mensaje = (
            "Ocurrió un error inesperado al consultar la prioridad."
        )

    return {
        "asignada": False,
        "prioridad": None,
        "justificacion": mensaje,
        "tipo_regla": "microservicio",
        "origen": "MENSAJERIA_DEL_VALLE"
    }

import json
import os

from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


PRIORIDADES_VALIDAS = {"Alta", "Media", "Baja"}


def consultar_prioridad_cliente(
    tipo_documento: str,
    numero_documento_cliente: str,
    tipo_solicitud: str
) -> dict:

    url = os.getenv("MENSAJERIA_PRIORIDAD_URL")

    if not url:
        return {
            "asignada": False,
            "prioridad": None,
            "justificacion": (
                "No está configurada la URL del microservicio."
            )
        }

    if not all([
        tipo_documento,
        numero_documento_cliente,
        tipo_solicitud
    ]):
        return {
            "asignada": False,
            "prioridad": None,
            "justificacion": (
                "Faltan datos obligatorios para consultar "
                "la prioridad del cliente."
            )
        }

    datos = {
        "tipo_documento": tipo_documento,
        "numero_documento_cliente": numero_documento_cliente,
        "tipo_solicitud": tipo_solicitud
    }

    try:
        contenido = json.dumps(datos).encode("utf-8")

        solicitud = Request(
            url,
            data=contenido,
            headers={
                "Content-Type": "application/json"
            },
            method="POST"
        )

        with urlopen(solicitud, timeout=5) as respuesta:
            resultado = json.loads(
                respuesta.read().decode("utf-8")
            )

        if not isinstance(resultado, dict):
            raise ValueError("Respuesta JSON inválida")

        prioridad = resultado.get("prioridad")
        justificacion = resultado.get("justificacion")
        perfil_cliente = resultado.get("perfil_cliente")

        if prioridad not in PRIORIDADES_VALIDAS:
            raise ValueError(
                "El servicio devolvió una prioridad inválida"
            )

        if (
            not isinstance(justificacion, str)
            or not justificacion.strip()
        ):
            raise ValueError(
                "El servicio no devolvió una justificación válida"
            )

        if (
            perfil_cliente is not None
            and (
                not isinstance(perfil_cliente, str)
                or not perfil_cliente.strip()
            )
        ):
            raise ValueError(
                "El perfil del cliente devuelto no es válido"
            )

        return {
            "asignada": True,
            "prioridad": prioridad,
            "justificacion": justificacion,
            "tipo_regla": "microservicio",
            "origen": "MENSAJERIA_DEL_VALLE",
            "perfil_cliente": perfil_cliente
        }

    except HTTPError as error:
        mensaje = (
            f"El microservicio respondió con HTTP {error.code}"
        )

    except URLError:
        mensaje = (
            "No fue posible conectar con el microservicio."
        )

    except TimeoutError:
        mensaje = (
            "El microservicio superó el tiempo de espera."
        )

    except (ValueError, json.JSONDecodeError):
        mensaje = (
            "El microservicio devolvió una respuesta inválida."
        )

    except Exception:
        mensaje = (
            "Ocurrió un error inesperado al consultar la prioridad."
        )

    return {
        "asignada": False,
        "prioridad": None,
        "justificacion": mensaje,
        "tipo_regla": "microservicio",
        "origen": "MENSAJERIA_DEL_VALLE"
    }
