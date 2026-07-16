from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class UploadResponse(BaseModel):
    file_id: str
    filename: str
    mime_type: str
    status: str
    message: str
    size_bytes: int
    created_at: datetime


class NominaExtraction(BaseModel):
    nombre_trabajador: Optional[str] = Field(None, description="Nombre completo del empleado")
    nombre_empresa: Optional[str] = Field(None, description="Nombre de la empresa")
    ingresos_brutos: Optional[float] = Field(None, description="Total devengado/bruto")
    ingresos_netos: Optional[float] = Field(None, description="Total neto a percibir")
    fecha_nomina: Optional[str] = Field(None, description="Período de la nómina (MM/YYYY o DD/MM/YYYY)")
    iban: Optional[str] = Field(None, description="IBAN completo (24 caracteres, empieza por ES)")
    confidence: str = Field("high", description="high | medium | low")
    raw_llm_response: Optional[str] = Field(None, description="Respuesta cruda del LLM")


class ExtractionMetadata(BaseModel):
    """Metadata del proceso OCR/LLM."""
    file_id: str
    filename: str
    llm_confidence: str
    raw_llm_response: Optional[str] = None


class ValidationResult(BaseModel):
    """
    Resultado de la extracción + validación de una nómina.
    """
    validated_data: Dict[str, Any]
    flags: List[Dict[str, str]]
    overall_confidence: str  # high | medium | low
    status: str  # validated | needs_review | error
    flag_count: Dict[str, int]
    extraction_metadata: Optional[ExtractionMetadata] = None
