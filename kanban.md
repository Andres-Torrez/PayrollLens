# 🏗️ NominaAI — Kanban de Proyecto

> **Proyecto:** Extractor inteligente de nóminas con OCR + LLM + validación de datos.  
> **Stack:** FastAPI (Python) + Next.js 14 + Tailwind + shadcn/ui + GPT-4o Vision + SQLite.  
> **Herramientas:** Cursor (IDE), Kimi Claw (asistente IA), GitHub (repo + Projects).  
> **Tiempo estimado:** 30-60 minutos de trabajo real por tarea.  
> **Meta:** Entregar un producto que demuestre cómo trabajamos con IA, cómo manejamos que "el LLM a veces falla", y cómo validamos resultados.

---

## 📋 Columnas del Tablero

| Backlog | 🚧 En Progreso | 👀 Review | ✅ Done |
|---------|---------------|-----------|---------|
| Tareas pendientes | Tarea activa (máx 1) | Hecho, esperando test/merge | Completado y mergeado |

---

## 📋 BACKLOG — Tareas

---

### 1. 🏗️ Arquitectura & Setup: Cimiento del Proyecto

**Objetivo:** Crear el repositorio `nomina-ai`, definir la estructura de carpetas profesional (backend FastAPI / frontend Next.js), configurar `.gitignore` robusto, y subir el primer commit. Este es el cimiento: si la estructura es limpia, todo lo demás fluye.

**Tareas:**
- [ ] Crear repositorio en GitHub (público o privado según prefieras)
- [ ] Clonar localmente y crear estructura de carpetas:
  - `backend/app/{routes,services,models,db}/`
  - `frontend/` (vacío por ahora, se inicializa en tarea 7)
- [ ] Crear `.gitignore` completo (Python + Node + OS + uploads)
- [ ] Crear `README.md` inicial con visión del producto y stack técnico
- [ ] Crear `backend/requirements.txt` vacío y `backend/.env.example`
- [ ] Primer commit: `chore: initial project structure`
- [ ] Activar GitHub Projects en el repo y crear columnas: Backlog / En Progreso / Review / Done

**Criterios de aceptación:**
- [ ] `git clone` + `ls` muestra una estructura profesional que no da vergüenza mostrar en la entrevista
- [ ] No hay archivos basura trackeados (verificar con `git status`)
- [ ] El `.gitignore` cubre `__pycache__`, `node_modules`, `.env`, y `uploads/`

**Labels:** `setup` `backend` `frontend` `sprint-1`  
**Rama:** `setup/initial-structure`

---

### 2. ⚡ API Base: Primer Endpoint Vivo

**Objetivo:** Levantar FastAPI con un endpoint `/health` que responda `{"status": "ok", "service": "nomina-ai"}`. Configurar CORS, logging básico, y estructura de routers. El objetivo es tener un backend que "respire" antes de meterle lógica de negocio.

**Tareas:**
- [ ] Instalar dependencias base: `fastapi`, `uvicorn`, `python-multipart`, `python-dotenv`
- [ ] Crear `backend/app/main.py` con app FastAPI instanciada
- [ ] Configurar CORS para permitir peticiones desde `localhost:3000`
- [ ] Crear router base con endpoint `GET /health`
- [ ] Configurar logging básico (uvicorn default)
- [ ] Documentar en `README.md` cómo levantar el backend: `uvicorn app.main:app --reload --port 8000`
- [ ] Probar con `curl http://localhost:8000/health` y capturar respuesta

**Criterios de aceptación:**
- [ ] `curl http://localhost:8000/health` devuelve `{"status": "ok", "service": "nomina-ai"}`
- [ ] La documentación automática de FastAPI (`/docs`) está accesible
- [ ] El backend levanta sin errores en puerto 8000

**Labels:** `backend` `fastapi` `api` `sprint-1`  
**Rama:** `backend/api-base`

---

### 3. 📤 Subida de Archivos: Drag, Drop & Guardar

**Objetivo:** Endpoint `POST /api/upload` que reciba PDF o imagen (JPEG/PNG), valide el tipo MIME, limite a 10MB, y guarde el archivo temporalmente en `backend/uploads/`. Debe devolver un `file_id` único (UUID) para trackear el documento durante todo el flujo.

**Tareas:**
- [ ] Crear directorio `backend/uploads/` (agregarlo a `.gitignore` si no está)
- [ ] Crear endpoint `POST /api/upload` en `backend/app/routes/upload.py`
- [ ] Validar tipos MIME permitidos: `application/pdf`, `image/jpeg`, `image/png`
- [ ] Validar tamaño máximo: 10MB (rechazar con 413 si excede)
- [ ] Generar `file_id` único con `uuid.uuid4()` al guardar el archivo
- [ ] Guardar archivo con nombre seguro: `{file_id}_{original_filename}`
- [ ] Responder con JSON: `{"file_id": "...", "filename": "...", "status": "received", "mime_type": "..."}`
- [ ] Manejar errores: archivo vacío, formato no soportado, tamaño excedido
- [ ] Testear con Postman/curl subiendo un PDF real

**Criterios de aceptación:**
- [ ] Subir una nómina PDF devuelve `{"file_id": "abc-123", "status": "received"}` con 200
- [ ] Subir un .exe devuelve 400 con mensaje claro
- [ ] Subir un archivo de 15MB devuelve 413
- [ ] El archivo se guarda físicamente en `backend/uploads/` y se puede abrir

**Labels:** `backend` `api` `upload` `file-handling` `sprint-1`  
**Rama:** `backend/upload-endpoint`

---

### 4. 🧠 OCR Inteligente: El Cerebro del Extractor

**Objetivo:** Integrar GPT-4o Vision (o Claude 3) para leer el archivo subido. Diseñar un **prompt estructurado** que pida explícitamente: nombre del trabajador, empresa, ingresos brutos, ingresos netos, fecha, IBAN. El prompt debe incluir instrucciones de formato JSON y advertencias sobre campos borrosos o ilegibles.

**Tareas:**
- [ ] Instalar cliente OpenAI: `pip install openai`
- [ ] Crear `backend/app/services/ocr.py` con función `extract_from_file(file_id, file_path)`
- [ ] Leer archivo como base64 para enviar a GPT-4o Vision
- [ ] Diseñar prompt detallado:
  - "Eres un extractor de datos de nóminas españolas..."
  - "Extrae: nombre_trabajador, nombre_empresa, ingresos_brutos, ingresos_netos, fecha_nomina, iban"
  - "Si un campo es ilegible o dudoso, indícalo con confidence: low"
  - "Responde ÚNICAMENTE en JSON válido"
- [ ] Parsear respuesta del LLM a diccionario Python
- [ ] Guardar la respuesta cruda (raw JSON) en la base de datos para análisis
- [ ] Manejar errores de parsing: si el LLM no devuelve JSON válido, capturar y loggear
- [ ] Documentar el prompt exacto en `README.md` o comentarios

**Criterios de aceptación:**
- [ ] El LLM devuelve un JSON estructurado con los 6 campos solicitados
- [ ] Si el campo "IBAN" está borroso, el JSON incluye `confidence: "low"` para ese campo
- [ ] Si el LLM devuelve texto plano en vez de JSON, se captura el error sin crashear el servidor
- [ ] La respuesta cruda se guarda para poder debuggear después

**Labels:** `backend` `ai` `ocr` `llm` `prompt-engineering` `sprint-1`  
**Rama:** `backend/ocr-inteligente`

---

### 5. 🔍 Validación de Datos: Cuando la IA Miente

**Objetivo:** Construir el módulo `backend/app/services/validator.py` con reglas de negocio que verifiquen la coherencia de los datos extraídos por el LLM. No rechazamos todo si falla algo: marcamos el campo como `confidence: "low"` y pedimos revisión humana. Esto es lo que diferencia un MVP de un producto real.

**Tareas:**
- [ ] Crear `backend/app/services/validator.py`
- [ ] Implementar validación de IBAN: longitud 24, empieza por ES, dígitos de control válidos
- [ ] Implementar validación lógica: ingresos_netos < ingresos_brutos (si no, flaggear)
- [ ] Implementar validación de fecha: formato válido, no futura, no anterior a 2020
- [ ] Implementar validación de nombre: no vacío, al menos 2 palabras (nombre + apellido)
- [ ] Implementar validación de empresa: no vacío, más de 2 caracteres
- [ ] Crear función `validate_extraction(raw_data)` que devuelva:
  - `validated_data` con los campos corregidos
  - `flags` array con los campos dudosos y por qué
  - `overall_confidence`: "high" / "medium" / "low"
- [ ] Integrar validador en el endpoint de upload (post-OCR)
- [ ] Loggear qué validaciones fallaron para análisis posterior

**Criterios de aceptación:**
- [ ] Una nómina con IBAN mal escrito por el LLM es detectada y flaggeada, no pasada como válida
- [ ] Si netos > brutos, se marca `confidence: "low"` en ambos campos con razón "incoherencia lógica"
- [ ] Una fecha como "32/13/2024" es detectada como inválida
- [ ] El validador nunca crashea: si falta un campo, lo marca como `missing` y continúa

**Labels:** `backend` `validation` `data-quality` `sprint-1`  
**Rama:** `backend/validacion-datos`

---

### 6. 🗄️ Persistencia: SQLite & Modelo de Datos

**Objetivo:** Definir el esquema SQLAlchemy con tabla `extractions` que guarde cada dato extraído, el estado del proceso, el JSON crudo del LLM, y los flags de validación. Endpoint `GET /api/extractions/{id}` para recuperar un resultado completo.

**Tareas:**
- [ ] Instalar SQLAlchemy: `pip install sqlalchemy`
- [ ] Crear `backend/app/db/database.py` con engine SQLite y SessionLocal
- [ ] Definir modelo SQLAlchemy `Extraction` con campos:
  - `id` (UUID, PK)
  - `filename` (str)
  - `mime_type` (str)
  - `nombre_trabajador` (str, nullable)
  - `nombre_empresa` (str, nullable)
  - `ingresos_brutos` (float, nullable)
  - `ingresos_netos` (float, nullable)
  - `fecha_nomina` (str, nullable)
  - `iban` (str, nullable)
  - `raw_llm_response` (text)
  - `validation_flags` (JSON/text)
  - `overall_confidence` (str: high/medium/low)
  - `status` (str: pending/processing/validated/needs_review/error)
  - `created_at`, `updated_at` (timestamps)
- [ ] Crear endpoint `GET /api/extractions/{file_id}`
- [ ] Crear endpoint `GET /api/extractions` (listado paginado opcional)
- [ ] Integrar creación de registro en el flujo de upload (antes de OCR, actualizar status)
- [ ] Crear las tablas automáticamente al iniciar la app

**Criterios de aceptación:**
- [ ] Después de subir una nómina, `GET /api/extractions/{file_id}` devuelve todos los datos
- [ ] El campo `raw_llm_response` contiene el JSON exacto que devolvió el LLM
- [ ] Si la validación falla, `status` es `needs_review` y `validation_flags` no está vacío
- [ ] La base de datos se crea automáticamente al primer `uvicorn`

**Labels:** `backend` `database` `sqlite` `sqlalchemy` `sprint-1`  
**Rama:** `backend/persistencia-sqlite`

---

### 7. 🎨 Frontend: UI de Subida (Dropzone)

**Objetivo:** Componente React con drag-and-drop para subir nóminas. Mostrar preview del archivo, estados visuales claros (idle → dragging → uploading → processing → done), y diseño limpio con Tailwind + shadcn/ui. Primera impresión profesional.

**Tareas:**
- [ ] Inicializar proyecto Next.js 14: `npx shadcn@latest init --yes --template next --base-color slate`
- [ ] Instalar `react-dropzone` y `lucide-react`
- [ ] Crear componente `UploadZone` en `frontend/components/upload-zone.tsx`
- [ ] Implementar drag-and-drop con feedback visual:
  - Borde punteado animado al arrastrar
  - Icono de archivo + nombre al soltar
  - Spinner/loader durante subida
  - Check verde al completar
- [ ] Conectar con endpoint `POST /api/upload` del backend
- [ ] Manejar errores: archivo muy grande, formato no soportado, error de red
- [ ] Mostrar `file_id` recibido al completar
- [ ] Responsive: debe verse bien en móvil y desktop

**Criterios de aceptación:**
- [ ] Arrastrar una nómina al navegador inicia el flujo con feedback visual en cada paso
- [ ] Un archivo .exe muestra error visual inmediato sin llegar al backend
- [ ] En móvil (375px de ancho) la zona de drop no se rompe
- [ ] Al completar, se muestra el `file_id` y un botón "Ver resultado"

**Labels:** `frontend` `nextjs` `ui` `upload` `sprint-1`  
**Rama:** `frontend/dropzone-ui`

---

### 8. 📊 Frontend: Dashboard de Resultados

**Objetivo:** Pantalla que muestre los datos extraídos en tarjetas organizadas y legibles. Si un campo tiene `confidence: "low"`, se resalta en naranja con icono de advertencia. Botón "Reintentar extracción" si el usuario detecta algo raro. Esto es donde el usuario decide si confía en la IA.

**Tareas:**
- [ ] Crear componente `ExtractionResult` en `frontend/components/extraction-result.tsx`
- [ ] Crear página `frontend/app/result/[file_id]/page.tsx`
- [ ] Fetch a `GET /api/extractions/{file_id}` al cargar la página
- [ ] Mostrar campos en grid/tarjetas: Nombre, Empresa, Ingresos Brutos, Ingresos Netos, Fecha, IBAN
- [ ] Resaltar campos con `confidence: "low"`:
  - Fondo naranja claro
  - Icono `AlertTriangle` de lucide-react
  - Tooltip con la razón del flag
- [ ] Mostrar `overall_confidence` como badge (verde/amarillo/rojo)
- [ ] Botón "Reintentar extracción" que vuelva a llamar al OCR
- [ ] Estado de carga skeleton mientras se carga el resultado
- [ ] Estado de error si el `file_id` no existe

**Criterios de aceptación:**
- [ ] Ver una nómina procesada con todos los datos bonitos y bien espaciados
- [ ] Ver un campo dudoso (ej. IBAN) resaltado visualmente con explicación
- [ ] El badge de confianza general es visible sin hacer scroll
- [ ] El botón "Reintentar" funciona y actualiza los datos sin recargar la página

**Labels:** `frontend` `nextjs` `dashboard` `ui` `sprint-1`  
**Rama:** `frontend/resultados-dashboard`

---

### 9. 🎭 Estados de Carga & Empty States

**Objetivo:** Manejar TODOS los estados UX posibles: loading skeleton mientras la IA piensa, empty state si no hay extracciones previas, error si el archivo es inválido o el servidor falla, y éxito con animación sutil. No dejar al usuario en la oscuridad nunca.

**Tareas:**
- [ ] Crear componente `LoadingSkeleton` para la pantalla de resultados
- [ ] Crear componente `EmptyState` para la página principal (sin archivos subidos)
  - Ilustración/icono amigable
  - Texto: "Sube tu primera nómina para empezar"
- [ ] Crear componente `ErrorState` reutilizable:
  - Error de red (backend caído)
  - Error de archivo (formato/tamaño)
  - Error de extracción (OCR falló)
- [ ] Crear componente `SuccessAnimation` (check animado o confeti sutil)
- [ ] Implementar toast notifications con `sonner` o `react-hot-toast`
- [ ] Asegurar que no hay pantallas en blanco en ningún flujo
- [ ] Testear cada estado manualmente

**Criterios de aceptación:**
- [ ] Cada estado tiene su propio diseño distintivo (no genérico)
- [ ] No hay pantallas en blanco ni errores crudos del navegador en ningún caso
- [ ] El usuario sabe siempre qué está pasando y qué puede hacer
- [ ] Los toasts no se acumulan (máximo 3 visibles)

**Labels:** `frontend` `ux` `states` `sprint-1`  
**Rama:** `frontend/estados-ux`

---

### 10. 🧪 Tests & Robustez: Romperlo para Arreglarlo

**Objetivo:** Tests unitarios para el validador y tests de integración para el endpoint de upload. Probar con PDFs reales, imágenes borrosas, y archivos corruptos. Documentar en qué casos el LLM falló y cómo lo mitigamos. Esto demuestra que pensamos en calidad, no solo en features.

**Tareas:**
- [ ] Instalar pytest: `pip install pytest pytest-asyncio httpx`
- [ ] Crear `backend/tests/test_validator.py` con casos:
  - IBAN válido vs inválido
  - Netos > brutos (debe flaggear)
  - Fecha inválida
  - Campo faltante
- [ ] Crear `backend/tests/test_upload.py` con casos:
  - Subida PDF válido (200)
  - Subida PNG válido (200)
  - Subida .exe (400)
  - Archivo > 10MB (413)
- [ ] Crear carpeta `backend/tests/fixtures/` con 3 archivos de prueba:
  - `nomina_ok.pdf` (nómina legible)
  - `nomina_borrosa.jpg` (imagen de baja calidad)
  - `corrupto.txt` (archivo no soportado)
- [ ] Documentar en `README.md` cómo correr tests: `pytest`
- [ ] Crear sección "Lecciones aprendidas" con ejemplos reales de fallos del LLM y cómo los corregimos

**Criterios de aceptación:**
- [ ] `pytest` pasa sin errores (todos los tests verdes)
- [ ] Hay al menos 3 casos de prueba para el validador
- [ ] Hay al menos 3 casos de prueba para el endpoint de upload
- [ ] El README tiene una sección "Lecciones aprendidas" con ejemplos reales de fallos del LLM

**Labels:** `backend` `testing` `qa` `pytest` `sprint-1`  
**Rama:** `qa/tests-robustez`

---

### 11. 📝 Documentación: La Historia del Proyecto

**Objetivo:** README profesional que cuente la historia completa del proyecto: arquitectura, decisiones técnicas, cómo instalar, cómo usar, y por qué hicimos cada elección. Esto es oro para la entrevista: demuestra que pensamos, no solo que copiamos.

**Tareas:**
- [ ] Descripción del proyecto y problema que resuelve (1 párrafo potente)
- [ ] Stack tecnológico con justificación de cada elección:
  - ¿Por qué FastAPI y no Flask?
  - ¿Por qué GPT-4o Vision y no Tesseract puro?
  - ¿Por qué Next.js 14 y no React vanilla?
  - ¿Por qué SQLite y no PostgreSQL para este challenge?
- [ ] Diagrama de arquitectura (Mermaid o imagen)
- [ ] Estructura completa de carpetas explicada línea a línea
- [ ] Comandos exactos de instalación y arranque (backend + frontend)
- [ ] Endpoints de la API con ejemplo de respuesta JSON real
- [ ] Esquema de base de datos (tabla extractions)
- [ ] Ejemplo del prompt enviado al LLM (código formateado)
- [ ] Estrategia de validación explicada
- [ ] Estado real honesto: qué funciona vs qué está pendiente
- [ ] Screenshots de la UI (subida + resultados)
- [ ] Cómo contribuir / estructura de PRs

**Criterios de aceptación:**
- [ ] Un tercero puede clonar, instalar y probar el proyecto en 5 minutos leyendo solo el README
- [ ] Las decisiones técnicas están justificadas, no son "porque sí"
- [ ] El prompt del LLM está documentado para que se vea cómo gestionamos fallos
- [ ] Hay al menos 2 screenshots de la aplicación funcionando
- [ ] El estado del proyecto es honesto: no hay features descritos como funcionando si no lo están

**Labels:** `docs` `readme` `sprint-1`  
**Rama:** `docs/readme-profesional`

---

### 12. 🚀 Polish Final: El Toque Maestro

**Objetivo:** Últimos detalles que elevan el proyecto de "funciona" a "brilla": favicon, título de página, animaciones de entrada, responsive design, manejo de errores con toast notifications, y modo oscuro opcional. Revisar que no haya `console.log` en producción ni claves API hardcodeadas.

**Tareas:**
- [ ] Añadir favicon y metadata (título, descripción) en `frontend/app/layout.tsx`
- [ ] Implementar animaciones de entrada con Framer Motion o CSS transitions
- [ ] Verificar responsive design en 3 breakpoints: 375px, 768px, 1440px
- [ ] Reemplazar todos los `console.log` por logs apropiados o eliminarlos
- [ ] Verificar que no hay claves API hardcodeadas en el frontend (usar `.env`)
- [ ] Añadir modo oscuro con `next-themes` (opcional pero suma puntos)
- [ ] Revisar contraste de colores (accesibilidad básica)
- [ ] Optimizar imágenes con `next/image`
- [ ] Revisar performance con Lighthouse (objetivo: +90 en Performance y Accessibility)
- [ ] Preparar demo script: 2 minutos mostrando subida, extracción, validación fallida, y corrección

**Criterios de aceptación:**
- [ ] Abrir la app en el móvil se ve bien y no hay scroll horizontal forzado
- [ ] No hay errores en consola del navegador en ningún flujo
- [ ] Lighthouse score >= 90 en Performance y Accessibility
- [ ] El demo script está ensayado y dura menos de 3 minutos
- [ ] Todo está listo para enseñar en la entrevista de 30 minutos

**Labels:** `frontend` `polish` `performance` `demo-ready` `sprint-1`  
**Rama:** `polish/toque-maestro`

---

## 🔄 Flujo de Trabajo (GitHub Flow)

1. Mover tarea a **🚧 En Progreso** (solo 1 a la vez)
2. Crear rama desde `main`: `git checkout -b nombre-de-la-rama`
3. Desarrollar con commits atómicos y mensajes claros
4. Push + crear Pull Request en GitHub
5. Mover tarea a **👀 Review**
6. Mergear a `main` cuando esté listo
7. Mover tarea a **✅ Done**
8. Pasar a la siguiente tarea

---

## 🎯 Demo Script (para la entrevista de 30 min)

1. **Subida (30 seg):** Arrastrar nómina PDF → feedback visual
2. **Procesamiento (1 min):** Mostrar logs del backend, el prompt enviado al LLM
3. **Resultado (1 min):** Dashboard con datos extraídos, campo IBAN resaltado en naranja
4. **Validación (1 min):** Explicar por qué flaggeó: "El LLM leyó mal el IBAN, el validador detectó que no cumple checksum"
5. **Corrección (30 seg):** Click en "Reintentar", mostrar cómo mejora
6. **Lecciones (30 seg):** "Esto es lo que evalúan: no que funcione perfecto, sino cómo manejamos que la IA se equivoque"

---

> **Nota para Cursor:** Este archivo es el contexto completo del proyecto. Cada tarea se trabaja en una rama independiente. El objetivo final es demostrar a Kontaktu que sabemos trabajar con IA, manejar fallos del LLM, y construir productos con calidad de producción.
