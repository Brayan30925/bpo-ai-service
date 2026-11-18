
from app.services.validador import validar_solicitud
from app.services.decision_service import determinar_siguiente_paso
from app.services.prioridad import asignar_prioridad
from app.services.clasificador import clasificar_solicitud


def test_validar_solicitud_completa():
    descripcion = (
        "Desde ayer tengo una falla en la estufa "
        "y necesito que realicen una reparación."
    )

    resultado = validar_solicitud(descripcion)

    assert resultado["valida"] is True
    assert resultado["faltantes"] == []


def test_validar_solicitud_sin_fecha():
    descripcion = (
        "Tengo una falla en la estufa "
        "y necesito que realicen una reparación."
    )

    resultado = validar_solicitud(descripcion)

    assert resultado["valida"] is False
    assert "Cuándo ocurrió" in resultado["faltantes"]


def test_cierre_por_informacion_insuficiente():
    resultado = determinar_siguiente_paso(
        False,
        {},
        {}
    )

    assert resultado["proximo_paso"] == (
        "CIERRE_POR_INFORMACION_INSUFICIENTE"
    )
    assert resultado["estado"] == "cerrado"


def test_gestion_externa():
    configuracion = {
        "delegaciones": {
            "Incidente técnico": {
                "responsable": "EMPRESA",
                "proximo_paso": "GESTION_EXTERNA"
            }
        }
    }

    clasificacion = {
        "clasificada": True,
        "categoria": "Incidente técnico"
    }

    resultado = determinar_siguiente_paso(
        True,
        clasificacion,
        configuracion
    )

    assert resultado["proximo_paso"] == "GESTION_EXTERNA"
    assert resultado["estado"] == "pendiente"


def test_respuesta_directa():
    configuracion = {
        "delegaciones": {
            "Consulta informativa": {
                "responsable": "BPO",
                "proximo_paso": "RESPUESTA_DIRECTA"
            }
        }
    }

    clasificacion = {
        "clasificada": True,
        "categoria": "Consulta informativa"
    }

    resultado = determinar_siguiente_paso(
        True,
        clasificacion,
        configuracion
    )

    assert resultado["proximo_paso"] == "RESPUESTA_DIRECTA"
    assert resultado["estado"] == "pendiente_respuesta"


def test_prioridad_alta_por_reglas():
    resultado = asignar_prioridad(
        empresa="GASES DEL ORINOCO",
        descripcion=(
            "Tengo una fuga urgente en la estufa "
            "y necesito atención."
        )
    )

    assert resultado["asignada"] is True
    assert resultado["prioridad"] == "Alta"


def test_empresa_no_parametrizada():
    resultado = asignar_prioridad(
        empresa="EMPRESA INEXISTENTE",
        descripcion="Tengo un problema desde ayer."
    )

    assert resultado["asignada"] is False
    assert resultado["prioridad"] is None


def test_clasificador_con_respuesta_ia_simulada(monkeypatch):
    def respuesta_simulada(descripcion, categorias):
        return {
            "categoria": "Incidente técnico",
            "justificacion": "Clasificación simulada",
            "evidencia": ["falla"]
        }

    monkeypatch.setattr(
        "app.services.clasificador.clasificar_con_ia",
        respuesta_simulada
    )

    resultado = clasificar_solicitud(
        "GASES DEL ORINOCO",
        "Tengo una falla en la estufa."
    )

    assert resultado["clasificada"] is True
    assert resultado["categoria"] == "Incidente técnico"
    assert resultado["metodo"] == "IA_GROQ"


def test_clasificador_usa_reglas_si_ia_falla(monkeypatch):
    def error_simulado(descripcion, categorias):
        raise RuntimeError("Servicio de IA no disponible")

    monkeypatch.setattr(
        "app.services.clasificador.clasificar_con_ia",
        error_simulado
    )

    resultado = clasificar_solicitud(
        "GASES DEL ORINOCO",
        "Tengo una falla en la estufa."
    )

    assert resultado["clasificada"] is True
    assert resultado["categoria"] == "Incidente técnico"
    assert resultado["metodo"] == "REGLAS"

