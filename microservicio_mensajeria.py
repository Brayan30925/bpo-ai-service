
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


app = FastAPI(
    title="Microservicio de Prioridades",
    description="Servicio simulado de MENSAJERÍA DEL VALLE",
    version="2.0.0"
)


class SolicitudPrioridad(BaseModel):
    tipo_documento: str = Field(min_length=1)
    numero_documento_cliente: str = Field(min_length=1)
    tipo_solicitud: str = Field(min_length=1)


# Clientes ficticios para las pruebas.
# La llave combina tipo y número de documento.
CLIENTES = {
    ("CC", "102045678"): {
        "perfil": "preferencial",
        "prioridades": {
            "Incidente técnico": "Alta",
            "Solicitud administrativa": "Media",
            "Consulta informativa": "Baja"
        }
    },
    ("CC", "123456789"): {
        "perfil": "estandar",
        "prioridades": {
            "Incidente técnico": "Media",
            "Solicitud administrativa": "Baja",
            "Consulta informativa": "Baja"
        }
    },
    ("NIT", "900123456"): {
        "perfil": "corporativo",
        "prioridades": {
            "Incidente técnico": "Alta",
            "Solicitud administrativa": "Alta",
            "Consulta informativa": "Media"
        }
    }
}


@app.get("/")
def inicio():
    return {
        "servicio": "Prioridades MENSAJERÍA DEL VALLE",
        "version": "2.0.0",
        "estado": "activo"
    }


@app.post("/prioridad")
def determinar_prioridad(solicitud: SolicitudPrioridad):

    tipo_documento = solicitud.tipo_documento.strip().upper()
    numero_documento = solicitud.numero_documento_cliente.strip()
    tipo_solicitud = solicitud.tipo_solicitud.strip()

    # Buscar al cliente usando tipo y número de documento.
    cliente = CLIENTES.get(
        (tipo_documento, numero_documento)
    )

    if cliente is None:
        raise HTTPException(
            status_code=404,
            detail="Cliente no registrado en el sistema simulado."
        )

    # Consultar la prioridad según el tipo de solicitud.
    prioridad = cliente["prioridades"].get(tipo_solicitud)

    if prioridad is None:
        raise HTTPException(
            status_code=422,
            detail="Tipo de solicitud no reconocido."
        )

    return {
        "prioridad": prioridad,
        "justificacion": (
            f"Prioridad {prioridad} asignada para el perfil "
            f"{cliente['perfil']} y la solicitud "
            f"{tipo_solicitud}."
        ),
        "perfil_cliente": cliente["perfil"]
    }
