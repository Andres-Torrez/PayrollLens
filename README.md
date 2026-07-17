# NominaFlow

Extracción inteligente de datos de nóminas españolas con OCR, visión por computador e inteligencia artificial generativa. El sistema no solo extrae información: detecta cuando la IA puede estar equivocada y marca los resultados para revisión humana.

---

## Tabla de contenidos

1. [Visión y alcance](#vision-y-alcance)
2. [Stack tecnológico](#stack-tecnologico)
3. [Arquitectura](#arquitectura)
4. [Estructura del proyecto](#estructura-del-proyecto)
5. [Requisitos previos](#requisitos-previos)
6. [Instalación y ejecución](#instalacion-y-ejecucion)
   - [Backend](#backend)
   - [Frontend](#frontend)
7. [Variables de entorno](#variables-de-entorno)
8. [API](#api)
9. [Estrategia de validación y guardrails](#estrategia-de-validacion-y-guardrails)
10. [Base de datos](#base-de-datos)
11. [Decisiones técnicas](#decisiones-tecnicas)
12. [Estado actual y próximos pasos](#estado-actual-y-proximos-pasos)
13. [Testing](#testing)
14. [Licencia](#licencia)

---

## Visión y alcance

NominaFlow permite a un usuario subir una nómina en formato PDF o imagen (JPEG/PNG) y obtener, de forma automatizada, los siguientes datos estructurados:

- Nombre del trabajador
- Nombre de la empresa
- Ingresos brutos
- Ingresos netos
- Fecha o período de la nómina
- IBAN

El diferenciador del producto es que **no confía ciegamente en la IA**. Cada extracción pasa por un motor de validación que verifica coherencia lógica, formato de campos y consistencia interna. Si algo falla, el resultado se marca como `needs_review` para revisión humana.

Este repositorio corresponde a un challenge técnico desarrollado para Kontaktu AI.

---

## Stack tecnológico

### Backend

| Tecnología | Propósito |
|---|---|
| Python 3.10+ | Lenguaje principal del servidor |
| FastAPI | Framework web moderno para la API REST |
| Uvicorn | Servidor ASGI de alto rendimiento |
| Pydantic 2 | Validación de modelos y contratos de API |
| SQLAlchemy 2.0 | ORM para persistencia en SQLite |
| SQLite | Base de datos embebida, sin infraestructura adicional |
| PyMuPDF | Renderizado de PDF a imágenes para el modelo de visión |
| OpenAI SDK (GitHub Models) | Cliente para llamar a modelos de lenguaje y visión |
| uv | Gestor de paquetes y entornos virtuales de Python |

### Frontend

| Tecnología | Propósito |
|---|---|
| Next.js 16 | Framework React con App Router |
| React 19 | Biblioteca de interfaces de usuario |
| TypeScript 5 | Tipado estático en todo el frontend |
| Tailwind CSS 4 | Framework de utilidades CSS |
| react-dropzone | Componente de arrastrar y soltar archivos |
| sonner | Notificaciones y toasts |
| lucide-react | Iconografía vectorial |

### Infraestructura y tooling

| Tecnología | Propósito |
|---|---|
| npm workspaces | Organización del monorepo frontend |
| Turbo | Orquestación de builds y tareas con caché |
| Prettier | Formateo de código |
| ESLint | Análisis estático de código |

---

## Arquitectura


Flujo resumido:

1. El usuario arrastra un archivo al navegador.
2. El frontend lo envía al backend y recibe un `file_id` único.
3. El backend convierte el PDF a imágenes y las envía al modelo de visión.
4. El modelo devuelve un JSON con los datos extraídos.
5. El motor de validación analiza cada campo y asigna un nivel de confianza.
6. El resultado se guarda en SQLite y se devuelve al frontend.

---

## Estructura del proyecto

```
.
├── backend/
│   ├── app/
│   │   ├── db/
│   │   │   ├── crud.py          # Operaciones contra SQLite
│   │   │   └── database.py      # Modelos SQLAlchemy y conexión
│   │   ├── models/
│   │   │   └── schemas.py       # Modelos Pydantic
│   │   ├── routes/
│   │   │   ├── extraction.py    # Endpoints de extracción y consulta
│   │   │   └── upload.py        # Endpoint de subida de archivos
│   │   ├── services/
│   │   │   ├── ocr.py           # Conversión PDF/imagen + llamada al LLM
│   │   │   └── validator.py     # Reglas de validación de negocio
│   │   └── main.py              # Punto de entrada de FastAPI
│   ├── uploads/                 # Archivos subidos temporalmente
│   ├── nominaflow.db            # Base de datos SQLite
│   ├── pyproject.toml           # Dependencias de Python
│   └── .env                     # Variables de entorno del backend
│
├── frontend/
│   └── next-monorepo/
│       ├── apps/web/
│       │   ├── app/
│       │   │   ├── page.tsx              # Pantalla principal
│       │   │   └── result/[fileId]/
│       │   │       └── page.tsx          # Pantalla de resultados
│       │   ├── components/
│       │   │   └── upload-zone.tsx       # Zona de arrastrar y soltar
│       │   ├── lib/
│       │   │   └── utils.ts              # Utilidades compartidas
│       │   └── next.config.ts            # Proxy hacia el backend
│       └── packages/ui/                  # Componentes compartidos del monorepo
│
├── README.md
└── kanban.md
```

---

## Requisitos previos

- Python 3.10 o superior
- Node.js 20 o superior
- npm 11 o superior
- Cuenta de GitHub con token de acceso para GitHub Models

---

## Instalación y ejecución

### Backend

1. Entra al directorio:

```bash
cd backend
```

2. Crea el entorno virtual e instala las dependencias con uv:

```bash
uv sync
```

3. Copia el archivo de ejemplo y configura tu token:

```bash
cp .env.example .env
```

Edita `.env` y añade tu token de GitHub Models:

```env
GITHUB_TOKEN=tu_token_aqui
```

4. Levanta el servidor:

```bash
uv run uvicorn app.main:app --reload --port 8001
```

La documentación interactiva de la API estará disponible en:

```
http://localhost:8001/docs
```

### Frontend

1. Entra al directorio:

```bash
cd frontend
```

2. Instala las dependencias:

```bash
npm install
```

3. Levanta el servidor de desarrollo:

```bash
npm run dev
```

La aplicación estará disponible en:

```
http://localhost:3000
```

El frontend está configurado para redirigir las peticiones a `/api/*` hacia el backend en `http://127.0.0.1:8001`.

---

## Variables de entorno

### Backend (.env)

| Variable | Descripción | Requerida |
|---|---|---|
| `GITHUB_TOKEN` | Token de GitHub para acceder a GitHub Models | Sí |
| `DATABASE_URL` | URL de conexión a la base de datos. Por defecto: SQLite local | No |

### Frontend

Actualmente la URL del backend está hardcodeada en `frontend/next-monorepo/apps/web/next.config.ts`. Se recomienda moverla a una variable de entorno en próximas iteraciones.

---

## API

### `POST /api/upload`

Sube un archivo PDF o imagen y devuelve un identificador único.

**Request:** `multipart/form-data` con el campo `file`.

**Response:**

```json
{
  "file_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "nomina_junio.pdf",
  "mime_type": "application/pdf",
  "status": "received",
  "message": "Archivo recibido correctamente. Procesando...",
  "size_bytes": 124578,
  "created_at": "2026-07-16T10:00:00"
}
```

### `POST /api/extract/{file_id}`

Procesa el archivo con OCR + LLM, valida los datos y guarda el resultado.

**Response:**

```json
{
  "validated_data": {
    "es_nomina": true,
    "nombre_trabajador": "Juan Pérez García",
    "nombre_empresa": "Acme SL",
    "ingresos_brutos": 2500.0,
    "ingresos_netos": 2000.0,
    "fecha_nomina": "06/2026",
    "iban": "ES9121000418450200051332"
  },
  "flags": [],
  "overall_confidence": "high",
  "status": "validated",
  "flag_count": {
    "errors": 0,
    "warnings": 0,
    "total": 0
  },
  "extraction_metadata": {
    "file_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "filename": "nomina_junio.pdf",
    "llm_confidence": "high",
    "raw_llm_response": "...",
    "saved_to_database": true
  }
}
```

### `GET /api/extractions/{file_id}`

Recupera una extracción previamente guardada.

### `GET /api/extractions`

Lista las extracciones guardadas, ordenadas por fecha descendente.

---

## Estrategia de validación y guardrails

El sistema implementa varias capas de control para reducir el riesgo de errores de la IA:

### 1. Clasificación del documento

Antes de extraer datos, el modelo de visión clasifica si el documento es realmente una nómina española mediante el campo `es_nomina`. Si el documento no es una nómina, el resultado se marca como `needs_review` y se omite la validación de campos individuales.

### 2. Validaciones de formato

- **IBAN**: debe tener 24 caracteres, comenzar por `ES` y contener solo dígitos tras el prefijo.
- **Fecha**: debe tener formato `MM/YYYY` o `DD/MM/YYYY`, no puede ser futura ni anterior a 2020.
- **Nombres**: al menos dos palabras y sin secuencias numéricas sospechosas.
- **Empresa**: no vacía, más de dos caracteres y no solo números.

### 3. Validaciones de coherencia

- Los ingresos netos deben ser menores que los brutos.
- Se alerta si la deducción es menor al 5% o mayor al 50%.
- Se detecta si netos y brutos son iguales.

### 4. Niveles de confianza

| Estado | Criterio |
|---|---|
| `high` | Sin errores ni advertencias |
| `medium` | Al menos una advertencia |
| `low` | Al menos un error |

El estado final puede ser `validated` o `needs_review`.

### 5. Auditoría

Cada respuesta cruda del LLM se almacena en el campo `raw_llm_response`, lo que permite investigar posteriormente por qué un campo fue extraído de cierta manera.

---

## Base de datos

Tabla principal: `extractions`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | TEXT (PK) | UUID del archivo |
| `filename` | TEXT | Nombre original del archivo |
| `mime_type` | TEXT | Tipo MIME |
| `size_bytes` | INTEGER | Tamaño en bytes |
| `es_nomina` | BOOLEAN | Indica si el documento es una nómina |
| `nombre_trabajador` | TEXT | Nombre del empleado |
| `nombre_empresa` | TEXT | Nombre de la empresa |
| `ingresos_brutos` | REAL | Ingresos brutos |
| `ingresos_netos` | REAL | Ingresos netos |
| `fecha_nomina` | TEXT | Período de la nómina |
| `iban` | TEXT | IBAN del trabajador |
| `raw_llm_response` | TEXT | Respuesta cruda del modelo |
| `validation_flags` | TEXT (JSON) | Flags de validación serializados |
| `overall_confidence` | TEXT | high / medium / low |
| `status` | TEXT | validated / needs_review / error |
| `created_at` | DATETIME | Fecha de creación |
| `updated_at` | DATETIME | Fecha de última actualización |

---

## Decisiones técnicas

### ¿Por qué FastAPI y no Flask?

FastAPI ofrece validación automática con Pydantic, documentación OpenAPI generada y soporte nativo para dependencias asíncronas. Esto reduce el código repetitivo y acelera el desarrollo de APIs tipadas.

### ¿Por qué GPT-4o Vision en lugar de OCR tradicional?

Las nóminas españolas tienen layouts muy variables. Un modelo de visión generalista entiende el contexto visual del documento, tolera escaneos de baja calidad y extrae información semántica sin necesidad de plantillas por empresa.

### ¿Por qué SQLite en lugar de PostgreSQL?

Para un challenge técnico y un MVP, SQLite elimina la necesidad de configurar un servidor de base de datos. Es portable, se versiona fácilmente en desarrollo y es suficiente para el volumen de datos esperado.

### ¿Por qué Next.js en lugar de React vanilla?

Next.js proporciona enrutamiento, optimización de fuentes e imágenes, y un proxy reverso útil para conectar frontend y backend durante el desarrollo sin problemas de CORS.

### ¿Por qué monorepo con npm workspaces y Turbo?

Permite separar la aplicación web de componentes y configuraciones compartidas, escalar a múltiples aplicaciones si es necesario y aprovechar el caché de builds de Turbo.

---

## Estado actual y próximos pasos

### Funcionalidades implementadas

- Subida de archivos PDF, JPEG y PNG con validación de tipo y tamaño.
- Extracción de datos mediante GPT-4o Vision.
- Validación de campos con reglas de negocio.
- Persistencia en SQLite con consulta de resultados.
- Frontend con drag-and-drop y pantalla de resultados.
- Guardrail de clasificación de documento no-nómina.

### Mejoras planificadas

- Forzar salida JSON válida del modelo mediante `response_format={"type": "json_object"}`.
- Validación completa del checksum del IBAN español.
- Rate limiting y logging estructurado.
- Tests unitarios e integración con pytest.
- Reintentos con backoff ante fallos del LLM.
- Capa de API centralizada en el frontend con manejo de errores robusto.
- Validación de respuestas de API con Zod.

---

## Testing

Actualmente no hay tests automatizados en el repositorio. Para añadirlos en el futuro:

```bash
cd backend
uv run pytest
```

Casos prioritarios a cubrir:

- Validador de IBAN, fechas e ingresos.
- Endpoint de subida con archivos válidos e inválidos.
- Clasificación de documentos que no son nóminas.

---

## Licencia

Este proyecto se desarrolla como parte de un challenge técnico y no tiene una licencia de código abierto definida. Todos los derechos pertenecen a su autor.
