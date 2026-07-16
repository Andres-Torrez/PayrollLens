from fastapi import APIRouter, HTTPException, status
from pathlib import Path

from app.services.ocr import extract_from_file
from app.services.validator import validate_extraction
from app.models.schemas import ValidationResult, ExtractionMetadata

router = APIRouter()

UPLOAD_DIR = Path("uploads")


@router.post(
    "/extract/{file_id}",
    response_model=ValidationResult,
    summary="Extraer y validar nómina",
    description=(
        "Extrae datos de la nómina con OCR/LLM y aplica reglas de validación "
        "(IBAN, ingresos, fecha, nombre, empresa). Devuelve validated_data + flags."
    ),
)
async def extract_and_validate(file_id: str):
    """
    Procesa un archivo subido con OCR y VALIDA los resultados.

    1. Busca el archivo en uploads/
    2. Extrae datos con GitHub Models (LLM)
    3. Valida con reglas de negocio (IBAN, ingresos, fecha...)
    4. Devuelve datos + flags de error + confianza global
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

    validation = validate_extraction(extraction)

    return ValidationResult(
        validated_data=validation["validated_data"],
        flags=validation["flags"],
        overall_confidence=validation["overall_confidence"],
        status=validation["status"],
        flag_count=validation["flag_count"],
        extraction_metadata=ExtractionMetadata(
            file_id=file_id,
            filename=file_path.name,
            llm_confidence=extraction.confidence,
            raw_llm_response=extraction.raw_llm_response,
        ),
    )
