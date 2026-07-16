import os
from pathlib import Path

from sqlalchemy import create_engine, Column, String, Float, DateTime, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite: ruta absoluta al directorio backend/ (no depende del CWD del proceso)
_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB_PATH = _BACKEND_DIR / "nominaflow.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH.as_posix()}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)

# Fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


class ExtractionDB(Base):
    """
    Tabla de extracciones guardadas en SQLite.
    Cada vez que procesamos una nómina, guardamos el resultado aquí.
    """
    __tablename__ = "extractions"

    id = Column(String, primary_key=True)  # UUID del file_id
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    size_bytes = Column(Integer, nullable=False)
    
    # Datos extraídos por el LLM
    nombre_trabajador = Column(String, nullable=True)
    nombre_empresa = Column(String, nullable=True)
    ingresos_brutos = Column(Float, nullable=True)
    ingresos_netos = Column(Float, nullable=True)
    fecha_nomina = Column(String, nullable=True)
    iban = Column(String, nullable=True)
    
    # Metadata del proceso
    raw_llm_response = Column(Text, nullable=True)  # Respuesta cruda del LLM
    validation_flags = Column(Text, nullable=True)  # JSON string con flags
    overall_confidence = Column(String, default="high")  # high | medium | low
    status = Column(String, default="pending")  # pending | validated | needs_review | error
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db():
    """
    Crea las tablas si no existen.
    Llamar al iniciar la aplicación.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Generador de sesiones para FastAPI (Dependency Injection).
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()