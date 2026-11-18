
import sqlite3
from pathlib import Path

db = Path("data/casos_externos.db")

conexion = sqlite3.connect(db)
conexion.row_factory = sqlite3.Row

registros = conexion.execute("""
    SELECT *
    FROM errores_integracion
    WHERE solicitud_id = ?
""", ("TEST-ERROR-001",)).fetchall()

for registro in registros:
    print(dict(registro))

conexion.close()
