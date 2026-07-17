import json
from sqlalchemy.orm import Session
from app.db.database import ExtractionDB
from app.models.schemas import NominaExtraction, ValidationResult
from datetime import datetime


def save_extraction(
    db: Session,
    file_id: str,
    filename: str,
    mime_type: str,
    size_bytes: int,
    extraction: NominaExtraction,
    validation: ValidationResult
):
    """
    Guarda una extracción validada en la base de datos.
    Si ya existe (mismo file_id), la actualiza.
    """
    db_extraction = db.query(ExtractionDB).filter(ExtractionDB.id == file_id).first()
    
    if db_extraction:
        # Actualizar existente
        db_extraction.es_nomina = extraction.es_nomina
        db_extraction.nombre_trabajador = extraction.nombre_trabajador
        db_extraction.nombre_empresa = extraction.nombre_empresa
        db_extraction.ingresos_brutos = extraction.ingresos_brutos
        db_extraction.ingresos_netos = extraction.ingresos_netos
        db_extraction.fecha_nomina = extraction.fecha_nomina
        db_extraction.iban = extraction.iban
        db_extraction.raw_llm_response = extraction.raw_llm_response
        db_extraction.validation_flags = json.dumps(validation.flags) if validation.flags else "[]"
        db_extraction.overall_confidence = validation.overall_confidence
        db_extraction.status = validation.status
        db_extraction.updated_at = datetime.utcnow()
    else:
        # Crear nuevo
        db_extraction = ExtractionDB(
            id=file_id,
            filename=filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            es_nomina=extraction.es_nomina,
            nombre_trabajador=extraction.nombre_trabajador,
            nombre_empresa=extraction.nombre_empresa,
            ingresos_brutos=extraction.ingresos_brutos,
            ingresos_netos=extraction.ingresos_netos,
            fecha_nomina=extraction.fecha_nomina,
            iban=extraction.iban,
            raw_llm_response=extraction.raw_llm_response,
            validation_flags=json.dumps(validation.flags) if validation.flags else "[]",
            overall_confidence=validation.overall_confidence,
            status=validation.status,
        )
        db.add(db_extraction)
    
    db.commit()
    db.refresh(db_extraction)
    return db_extraction


def get_extraction(db: Session, file_id: str):
    """
    Recupera una extracción por su file_id.
    """
    return db.query(ExtractionDB).filter(ExtractionDB.id == file_id).first()


def get_extractions(db: Session, skip: int = 0, limit: int = 100):
    """
    Lista todas las extracciones (paginado).
    Útil para un dashboard de historial.
    """
    return db.query(ExtractionDB).order_by(ExtractionDB.created_at.desc()).offset(skip).limit(limit).all()