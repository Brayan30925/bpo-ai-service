
import sqlite3
import uuid

from datetime import datetime, timezone
from pathlib import Path


# ==========================================================
# CONFIGURACION DE BASE DE DATOS
# ==========================================================

RUTA_PROYECTO = Path(__file__).resolve().parents[2]

RUTA_BASE_DATOS = (
    RUTA_PROYECTO / "data" / "casos_externos.db"
)


def obtener_conexion():
    """Crea una conexión con SQLite."""

    RUTA_BASE_DATOS.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conexion = sqlite3.connect(
        RUTA_BASE_DATOS,
        timeout=10
    )

    conexion.row_factory = sqlite3.Row

    return conexion


# ==========================================================
# INICIALIZACION Y ESTRUCTURA
# ==========================================================

def inicializar_base_datos():
    """Crea las tablas necesarias si no existen."""

    with obtener_conexion() as conexion:

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS casos_externos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caso_externo_id TEXT NOT NULL UNIQUE,
                empresa TEXT NOT NULL,
                solicitud_id TEXT NOT NULL,
                categoria TEXT NOT NULL,
                prioridad TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                estado TEXT NOT NULL,
                fecha_creacion TEXT NOT NULL,
                UNIQUE(empresa, solicitud_id)
            )
        """)

        conexion.execute("""
            CREATE TABLE IF NOT EXISTS errores_integracion (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa TEXT NOT NULL,
                solicitud_id TEXT NOT NULL,
                mensaje_error TEXT NOT NULL,
                numero_intentos INTEGER NOT NULL DEFAULT 1,
                estado TEXT NOT NULL DEFAULT 'PENDIENTE',
                fecha_error TEXT NOT NULL,
                UNIQUE(empresa, solicitud_id)
            )
        """)

        conexion.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_error_empresa_solicitud
            ON errores_integracion (
                empresa,
                solicitud_id
            )
        """)


def actualizar_estructura_base_datos():
    """
    Compatibilidad con bases de datos anteriores.
    Comprueba y crea el índice único de errores.
    """

    inicializar_base_datos()


# ==========================================================
# REGISTRO DE ERRORES
# ==========================================================

def registrar_error_integracion(
    empresa: str,
    solicitud_id: str,
    mensaje_error: str
) -> dict:
    """
    Registra un error o incrementa el contador
    de intentos de una solicitud existente.
    """

    inicializar_base_datos()

    fecha_error = datetime.now(
        timezone.utc
    ).isoformat()

    with obtener_conexion() as conexion:

        conexion.execute("""
            INSERT INTO errores_integracion (
                empresa,
                solicitud_id,
                mensaje_error,
                numero_intentos,
                estado,
                fecha_error
            )
            VALUES (?, ?, ?, 1, 'PENDIENTE', ?)

            ON CONFLICT(empresa, solicitud_id)
            DO UPDATE SET
                mensaje_error = excluded.mensaje_error,
                numero_intentos =
                    errores_integracion.numero_intentos + 1,
                estado = 'PENDIENTE',
                fecha_error = excluded.fecha_error
        """, (
            empresa,
            solicitud_id,
            mensaje_error,
            fecha_error
        ))

        registro = conexion.execute("""
            SELECT numero_intentos, estado
            FROM errores_integracion
            WHERE empresa = ?
              AND solicitud_id = ?
        """, (
            empresa,
            solicitud_id
        )).fetchone()

    return {
        "error_registrado": True,
        "estado_reintento": registro["estado"],
        "numero_intentos": registro["numero_intentos"]
    }


# ==========================================================
# RECUPERACION DE ERRORES
# ==========================================================

def marcar_error_solucionado(
    empresa: str,
    solicitud_id: str
) -> dict:
    """
    Marca como solucionado un error cuando
    la integración se completa correctamente.
    """

    inicializar_base_datos()

    with obtener_conexion() as conexion:

        cursor = conexion.execute("""
            UPDATE errores_integracion
            SET estado = 'SOLUCIONADO'
            WHERE empresa = ?
              AND solicitud_id = ?
              AND estado = 'PENDIENTE'
        """, (
            empresa,
            solicitud_id
        ))

    return {
        "error_actualizado": cursor.rowcount > 0,
        "estado": (
            "SOLUCIONADO"
            if cursor.rowcount > 0
            else None
        )
    }


# ==========================================================
# CREACION DE CASOS EXTERNOS
# ==========================================================

def crear_caso_externo(
    empresa: str,
    solicitud_id: str,
    descripcion: str,
    prioridad: str,
    categoria: str
) -> dict:
    """
    Simula la creación de un caso externo.

    Evita duplicados y detecta conflictos
    cuando una solicitud existente llega
    con información diferente.
    """

    inicializar_base_datos()

    caso = {
        "caso_externo_id": (
            f"EXT-{uuid.uuid4().hex[:8].upper()}"
        ),
        "empresa": empresa,
        "solicitud_id": solicitud_id,
        "categoria": categoria,
        "prioridad": prioridad,
        "descripcion": descripcion,
        "estado": "pendiente",
        "fecha_creacion": datetime.now(
            timezone.utc
        ).isoformat()
    }

    with obtener_conexion() as conexion:

        cursor = conexion.execute("""
            INSERT OR IGNORE INTO casos_externos (
                caso_externo_id,
                empresa,
                solicitud_id,
                categoria,
                prioridad,
                descripcion,
                estado,
                fecha_creacion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            caso["caso_externo_id"],
            caso["empresa"],
            caso["solicitud_id"],
            caso["categoria"],
            caso["prioridad"],
            caso["descripcion"],
            caso["estado"],
            caso["fecha_creacion"]
        ))

        duplicado = cursor.rowcount == 0

        registro = conexion.execute("""
            SELECT *
            FROM casos_externos
            WHERE empresa = ?
              AND solicitud_id = ?
        """, (
            empresa,
            solicitud_id
        )).fetchone()

        if registro is None:
            raise RuntimeError(
                "No fue posible recuperar el caso externo"
            )

        resultado = dict(registro)

    # Detectar si los datos recibidos son diferentes
    if duplicado:

        conflicto = (
            resultado["descripcion"] != descripcion
            or resultado["categoria"] != categoria
            or resultado["prioridad"] != prioridad
        )

        if conflicto:
            return {
                "integracion_exitosa": False,
                "caso_duplicado": True,
                "conflicto_detectado": True,
                "requiere_revision_manual": True,
                "mensaje": (
                    "La solicitud ya existe, pero contiene "
                    "información diferente. Requiere revisión manual."
                ),
                "caso_externo_id": resultado["caso_externo_id"]
            }

    return {
        "integracion_exitosa": True,
        "caso_duplicado": duplicado,
        "conflicto_detectado": False,
        **{
            clave: valor
            for clave, valor in resultado.items()
            if clave != "id"
        }
    }
