
import pytest

from app.services import integracion_service as servicio


@pytest.fixture
def base_datos_temporal(tmp_path, monkeypatch):
    ruta = tmp_path / "pruebas_integracion.db"

    monkeypatch.setattr(
        servicio,
        "RUTA_BASE_DATOS",
        ruta
    )

    servicio.inicializar_base_datos()

    return ruta


def crear_caso():
    return servicio.crear_caso_externo(
        empresa="GASES DEL ORINOCO",
        solicitud_id="TEST-001",
        descripcion="Tengo una falla desde ayer y necesito reparación.",
        prioridad="Media",
        categoria="Incidente técnico"
    )


def test_crear_caso_externo(base_datos_temporal):
    resultado = crear_caso()

    assert resultado["integracion_exitosa"] is True
    assert resultado["caso_duplicado"] is False
    assert resultado["conflicto_detectado"] is False
    assert resultado["caso_externo_id"].startswith("EXT-")
    assert resultado["estado"] == "pendiente"


def test_evitar_casos_duplicados(base_datos_temporal):
    primero = crear_caso()
    segundo = crear_caso()

    assert primero["caso_externo_id"] == segundo["caso_externo_id"]
    assert segundo["integracion_exitosa"] is True
    assert segundo["caso_duplicado"] is True

    import sqlite3

    with sqlite3.connect(base_datos_temporal) as conexion:
        cantidad = conexion.execute(
            "SELECT COUNT(*) FROM casos_externos"
        ).fetchone()[0]

    assert cantidad == 1


def test_detectar_conflicto_en_solicitud_existente(
    base_datos_temporal
):
    crear_caso()

    resultado = servicio.crear_caso_externo(
        empresa="GASES DEL ORINOCO",
        solicitud_id="TEST-001",
        descripcion="Desde hoy tengo una fuga urgente.",
        prioridad="Alta",
        categoria="Incidente técnico"
    )

    assert resultado["integracion_exitosa"] is False
    assert resultado["caso_duplicado"] is True
    assert resultado["conflicto_detectado"] is True
    assert resultado["requiere_revision_manual"] is True


def test_registrar_e_incrementar_errores(
    base_datos_temporal
):
    primero = servicio.registrar_error_integracion(
        "GASES DEL ORINOCO",
        "ERROR-001",
        "Servicio externo no disponible"
    )

    segundo = servicio.registrar_error_integracion(
        "GASES DEL ORINOCO",
        "ERROR-001",
        "Segundo intento fallido"
    )

    assert primero["error_registrado"] is True
    assert primero["numero_intentos"] == 1

    assert segundo["error_registrado"] is True
    assert segundo["numero_intentos"] == 2
    assert segundo["estado_reintento"] == "PENDIENTE"


def test_marcar_error_como_solucionado(
    base_datos_temporal
):
    servicio.registrar_error_integracion(
        "GASES DEL ORINOCO",
        "ERROR-002",
        "Fallo temporal"
    )

    resultado = servicio.marcar_error_solucionado(
        "GASES DEL ORINOCO",
        "ERROR-002"
    )

    assert resultado["error_actualizado"] is True
    assert resultado["estado"] == "SOLUCIONADO"

    segundo_intento = servicio.marcar_error_solucionado(
        "GASES DEL ORINOCO",
        "ERROR-002"
    )

    assert segundo_intento["error_actualizado"] is False
