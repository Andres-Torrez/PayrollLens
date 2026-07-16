from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UploadResponse(BaseModel):
    """
    Respuesta del endpoint de subida.
    El frontend recibe esto y sabe que el archivo fue recibido.
    """
    file_id: str          # UUID único para trackear este archivo
    filename: str           # Nombre original del archivo
    mime_type: str        # application/pdf, image/jpeg, image/png
    status: str           # "received", "processing", "done", "error"
    message: str          # Mensaje amigable para el usuario
    size_bytes: int       # Tamaño del archivo en bytes
    created_at: datetime  # Cuándo se subió