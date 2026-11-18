# Motor de Decisiones IA para BPO

Microservicio REST desarrollado con Python y FastAPI para automatizar la gestión y toma de decisiones sobre solicitudes recibidas por un BPO que presta servicios a diferentes empresas.

## 1. Objetivo

Automatizar el procesamiento de solicitudes mediante inteligencia artificial y reglas configurables por empresa.

El sistema realiza:

- Validación de información mínima.
- Clasificación de solicitudes.
- Asignación de prioridad.
- Determinación del siguiente paso operativo.
- Simulación de creación de casos externos.
- Prevención de casos duplicados.
- Registro y seguimiento de errores de integración.

## 2. Arquitectura

La solución utiliza una arquitectura modular:

- **FastAPI:** expone los servicios REST.
- **Validador:** comprueba que la solicitud contenga información suficiente.
- **Clasificador:** utiliza Groq y reglas alternativas.
- **Prioridad:** aplica reglas o consulta servicios externos.
- **Decision Service:** determina el siguiente paso operativo.
- **Integración Service:** registra casos externos y errores en SQLite.
- **Configuraciones JSON:** permiten parametrizar cada empresa.
- **Microservicio Mensajería:** simula un servicio externo de asignación de prioridades.

## 3. Tecnologías

- Python 3.12
- FastAPI
- Pydantic
- Groq
- SQLite
- Pytest
- HTTPX

## 4. Instalación

Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
cd bpo-ai-service
```

Crear entorno virtual:

```bash
py -3.12 -m venv .venv
```

Activar entorno virtual en Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## 5. Configuración

Crear una copia del archivo de ejemplo:

```powershell
Copy-Item .env.example .env
```

Editar `.env` y configurar:

```env
GROQ_API_KEY=TU_CLAVE_DE_GROQ
GROQ_MODEL=openai/gpt-oss-20b
MENSAJERIA_PRIORIDAD_URL=http://127.0.0.1:8001/prioridad
```

La clave de Groq debe mantenerse privada y nunca publicarse en Git.

## 6. Ejecución

Se requieren dos terminales de PowerShell.

### Terminal 1: Microservicio de Mensajería

Activar el entorno virtual y ejecutar:

```powershell
python -m uvicorn microservicio_mensajeria:app --host 127.0.0.1 --port 8001 --reload
```

### Terminal 2: Motor de decisiones BPO

Activar el entorno virtual y ejecutar:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Documentación interactiva:

http://127.0.0.1:8000/docs

Estado del servicio:

http://127.0.0.1:8000/health

## 7. Endpoints principales

| Método | Endpoint | Función |
|---|---|---|
| GET | `/` | Información del servicio |
| GET | `/health` | Estado del servicio |
| POST | `/solicitudes` | Procesamiento integral |
| POST | `/validar` | Validación de información |
| POST | `/clasificar` | Clasificación |
| POST | `/prioridad` | Asignación de prioridad |

## 8. Ejemplo de solicitud

```json
{
  "solicitud_id": "REQ-008",
  "empresa": "GASES DEL ORINOCO",
  "descripcion": "Desde ayer tengo una falla en la estufa y necesito que realicen una reparación.",
  "datos_adicionales": {
    "tipo_documento": "CC",
    "numero_documento_cliente": "102045678"
  }
}
```

La respuesta incluye la validación, clasificación, prioridad, siguiente paso y resultado de la integración cuando corresponda.

## 9. Pruebas

Ejecutar todas las pruebas automatizadas:

```powershell
python -m pytest -v
```

Las pruebas cubren validación, clasificación, prioridad, decisiones operativas, microservicio externo, prevención de duplicados y registro de errores.

## 10. Configuración para nuevas empresas

Cada empresa puede tener su propia configuración JSON dentro de:

`app/configurations/empresas/`

Esto permite incorporar categorías, reglas de prioridad y responsables operativos sin modificar el núcleo del motor.

## 11. Integraciones externas

La integración con plataformas de clientes se encuentra simulada para esta entrega.

El sistema contempla identificadores externos ficticios, control de duplicados y registro de errores para facilitar futuras conexiones con plataformas reales.

## 12. Seguridad y alcance

- Las claves y variables privadas se almacenan en `.env`.
- El archivo `.env` está excluido del repositorio.
- Los datos de clientes utilizados en las pruebas son ficticios.
- La creación de casos externos es simulada.

## 13. Ejecución local

La solución está diseñada para ejecutarse localmente. No requiere despliegue en la nube para las pruebas de esta entrega.