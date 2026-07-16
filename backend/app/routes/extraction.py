import json
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.crud import get_extraction, get_extractions, save_extraction
from app.db.database import get_db
from app.models.schemas import ExtractionMetadata, ExtractionRecord, ValidationResult
from app.routes.upload import UPLOAD_DIR
from app.services.ocr import extract_from_file
from app.services.validator import validate_extraction

router = APIRouter()

MIME_BY_SUFFIX = {
    ".pdf": "application/pdf",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
}


def _mime_from_path(file_path: Path) -> str:
    return MIME_BY_SUFFIX.get(file_path.suffix.lower(), "application/octet-stream")


def _record_to_dict(record) -> dict:
    return {
        "id": record.id,
        "filename": record.filename,
        "mime_type": record.mime_type,
        "size_bytes": record.size_bytes,
        "nombre_trabajador": record.nombre_trabajador,
        "nombre_empresa": record.nombre_empresa,
        "ingresos_brutos": record.ingresos_brutos,
        "ingresos_netos": record.ingresos_netos,
        "fecha_nomina": record.fecha_nomina,
        "iban": record.iban,
        "overall_confidence": record.overall_confidence,
        "status": record.status,
        "validation_flags": json.loads(record.validation_flags) if record.validation_flags else [],
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }


@router.post("/extract/{file_id}", response_model=ValidationResult)
async def extract_and_validate(file_id: str, db: Session = Depends(get_db)):
    """
    Procesa un archivo con OCR, VALIDA los resultados, y GUARDA en SQLite.
    """
    matching_files = list(UPLOAD_DIR.glob(f"{file_id}_*"))

    if not matching_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró archivo con file_id: {file_id}",
        )

    file_path = matching_files[0]

    try:
        extraction, _raw_response = extract_from_file(str(file_path))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error en OCR: {str(e)}",
        )

    validation_dict = validate_extraction(extraction)
    validation = ValidationResult(**validation_dict)

    save_extraction(
        db=db,
        file_id=file_id,
        filename=file_path.name,
        mime_type=_mime_from_path(file_path),
        size_bytes=file_path.stat().st_size,
        extraction=extraction,
        validation=validation,
    )

    validation.extraction_metadata = ExtractionMetadata(
        file_id=file_id,
        filename=file_path.name,
        llm_confidence=extraction.confidence,
        raw_llm_response=extraction.raw_llm_response,
        saved_to_database=True,
    )

    return validation


@router.get("/extractions/{file_id}", response_model=ExtractionRecord)
async def get_extraction_record(file_id: str, db: Session = Depends(get_db)):
    """
    Recupera una extracción guardada por su file_id.
    Útil para mostrar el resultado sin re-procesar el OCR.
    """
    record = get_extraction(db, file_id)

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró extracción con file_id: {file_id}",
        )

    return _record_to_dict(record)


@router.get("/extractions", response_model=List[ExtractionRecord])
async def list_extractions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Lista todas las extracciones guardadas (historial).
    Ordenadas por fecha descendente (las más nuevas primero).
    """
    records = get_extractions(db, skip=skip, limit=limit)
    return [_record_to_dict(record) for record in records]
