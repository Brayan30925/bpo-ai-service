
from fastapi.testclient import TestClient

from microservicio_mensajeria import app


cliente = TestClient(app)


def test_servicio_activo():
    respuesta = cliente.get("/")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "activo"


def test_cliente_preferencial():
    respuesta = cliente.post(
        "/prioridad",
        json={
            "tipo_documento": "CC",
            "numero_documento_cliente": "102045678",
            "tipo_solicitud": "Incidente técnico"
        }
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["prioridad"] == "Alta"
    assert respuesta.json()["perfil_cliente"] == "preferencial"


def test_cliente_corporativo():
    respuesta = cliente.post(
        "/prioridad",
        json={
            "tipo_documento": "NIT",
            "numero_documento_cliente": "900123456",
            "tipo_solicitud": "Solicitud administrativa"
        }
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["prioridad"] == "Alta"
    assert respuesta.json()["perfil_cliente"] == "corporativo"


def test_cliente_no_registrado():
    respuesta = cliente.post(
        "/prioridad",
        json={
            "tipo_documento": "CC",
            "numero_documento_cliente": "555555555",
            "tipo_solicitud": "Incidente técnico"
        }
    )

    assert respuesta.status_code == 404


def test_tipo_solicitud_no_reconocido():
    respuesta = cliente.post(
        "/prioridad",
        json={
            "tipo_documento": "CC",
            "numero_documento_cliente": "102045678",
            "tipo_solicitud": "Solicitud desconocida"
        }
    )

    assert respuesta.status_code == 422
