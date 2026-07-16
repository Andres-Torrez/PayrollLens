import uuid
import os
import shutil
import re
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from app.models.schemas import UploadResponse

# Router: agrupa endpoints relacionados
# prefix="/api" se añade en main.py
router = APIRouter()

# Tipos MIME permitidos
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
}

# Tamaño máximo: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 * 1024 KB = 10 MB

# Carpeta donde guardamos los archivos subidos
UPLOAD_DIR = Path("uploads")


@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint para subir una nómina (PDF o imagen).
    
    1. Valida tipo MIME (solo PDF, JPEG, PNG)
    2. Valida tamaño (máximo 10MB)
    3. Genera un file_id único (UUID)
    4. Guarda el archivo en uploads/
    5. Devuelve metadata para trackear el proceso
    """
    
    # --- Validación 1: ¿El archivo no está vacío? ---
    if file.filename is None or file.filename.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionó ningún archivo."
        )
    
    # --- Validación 2: ¿El tipo MIME es válido? ---
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de archivo no soportado: {file.content_type}. "
                f"Formatos permitidos: PDF, JPEG, PNG."
        )
    
    # --- Leer el contenido del archivo ---
    # Esto carga el archivo en memoria (RAM).
    # Para archivos de 10MB es perfectamente seguro.
    contents = await file.read()
    
    # --- Validación 3: ¿El archivo no está vacío? ---
    if len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El archivo está vacío."
        )
    
    # --- Validación 4: ¿No excede 10MB? ---
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Archivo demasiado grande: {len(contents)} bytes. "
                f"Máximo permitido: {MAX_FILE_SIZE} bytes (10MB)."
        )
    
    # --- Generar ID único y guardar ---
    file_id = str(uuid.uuid4())  # Ej: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    
    # Nombre seguro: file_id + nombre original sanitizado
    safe_original = re.sub(r'[^\w\s.-]', '', file.filename).replace(' ', '_')
    safe_filename = f"{file_id}_{safe_original}"
    file_path = UPLOAD_DIR / safe_filename

    # Guardar en disco
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # --- Respuesta al frontend ---
    return UploadResponse(
        file_id=file_id,
        filename=file.filename,
        mime_type=file.content_type,
        status="received",
        message="Archivo recibido correctamente. Procesando...",
        size_bytes=len(contents),
        created_at=datetime.utcnow()
    )