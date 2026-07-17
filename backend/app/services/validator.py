import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.models.schemas import NominaExtraction


class ValidationFlag:
    """
    Representa un problema detectado en un campo específico.
    """
    def __init__(self, field: str, reason: str, severity: str = "warning"):
        self.field = field
        self.reason = reason
        self.severity = severity  # "warning" o "error"
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "field": self.field,
            "reason": self.reason,
            "severity": self.severity
        }


def validate_iban(iban: Optional[str]) -> List[ValidationFlag]:
    """
    Valida un IBAN español.
    
    Reglas:
    - Debe tener exactamente 24 caracteres (sin espacios)
    - Debe empezar por "ES"
    - Dígitos de control básicos (solo formato, no checksum completo)
    """
    flags = []
    
    if iban is None or iban.strip() == "":
        flags.append(ValidationFlag("iban", "IBAN no detectado", "error"))
        return flags
    
    # Limpiar espacios
    clean = iban.replace(" ", "").replace("-", "").upper()
    
    if not clean.startswith("ES"):
        flags.append(ValidationFlag("iban", f"IBAN no empieza por ES: '{iban}'", "error"))
    
    if len(clean) != 24:
        flags.append(ValidationFlag("iban", f"IBAN debe tener 24 caracteres, tiene {len(clean)}: '{iban}'", "error"))
    
    if not clean[2:].isdigit():
        flags.append(ValidationFlag("iban", f"IBAN contiene caracteres no numéricos después de 'ES': '{iban}'", "error"))
    
    return flags


def validate_ingresos(brutos: Optional[float], netos: Optional[float]) -> List[ValidationFlag]:
    """
    Valida coherencia entre ingresos brutos y netos.
    
    Reglas:
    - Ambos deben ser números positivos
    - Netos DEBEN ser menores que brutos (si no, algo está mal)
    - La diferencia no debería ser excesiva (>50% de los brutos es sospechoso)
    """
    flags = []
    
    if brutos is None:
        flags.append(ValidationFlag("ingresos_brutos", "Ingresos brutos no detectados", "error"))
    elif brutos <= 0:
        flags.append(ValidationFlag("ingresos_brutos", f"Ingresos brutos deben ser positivos: {brutos}", "error"))
    
    if netos is None:
        flags.append(ValidationFlag("ingresos_netos", "Ingresos netos no detectados", "error"))
    elif netos <= 0:
        flags.append(ValidationFlag("ingresos_netos", f"Ingresos netos deben ser positivos: {netos}", "error"))
    
    # Regla clave: netos < brutos
    if brutos is not None and netos is not None:
        if netos > brutos:
            flags.append(ValidationFlag(
                "ingresos_netos", 
                f"Incoherencia lógica: netos ({netos}) > brutos ({brutos}). "
                f"Los ingresos netos siempre deben ser menores que los brutos.",
                "error"
            ))
        elif netos == brutos:
            flags.append(ValidationFlag(
                "ingresos_netos",
                f"Netos ({netos}) igual a brutos ({brutos}). Sin deducciones es sospechoso.",
                "warning"
            ))
        else:
            # Calcular porcentaje de deducción
            deduccion_pct = ((brutos - netos) / brutos) * 100
            if deduccion_pct > 50:
                flags.append(ValidationFlag(
                    "ingresos_brutos",
                    f"Deducción muy alta ({deduccion_pct:.1f}%). Verificar brutos/netos.",
                    "warning"
                ))
            elif deduccion_pct < 5:
                flags.append(ValidationFlag(
                    "ingresos_netos",
                    f"Deducción muy baja ({deduccion_pct:.1f}%). Verificar si faltan deducciones.",
                    "warning"
                ))
    
    return flags


def validate_fecha(fecha: Optional[str]) -> List[ValidationFlag]:
    """
    Valida la fecha de la nómina.
    
    Reglas:
    - Formato válido: MM/YYYY o DD/MM/YYYY
    - No puede ser fecha futura
    - No puede ser anterior a 2020 (nóminas muy antiguas son sospechosas)
    """
    flags = []
    
    if fecha is None or fecha.strip() == "":
        flags.append(ValidationFlag("fecha_nomina", "Fecha no detectada", "error"))
        return flags
    
    fecha_clean = fecha.strip()
    
    # Intentar parsear MM/YYYY
    parsed = None
    for fmt in ("%m/%Y", "%d/%m/%Y", "%m-%Y", "%d-%m-%Y"):
        try:
            parsed = datetime.strptime(fecha_clean, fmt)
            break
        except ValueError:
            continue
    
    if parsed is None:
        flags.append(ValidationFlag("fecha_nomina", f"Formato de fecha no reconocido: '{fecha}'. Esperado: MM/YYYY o DD/MM/YYYY", "error"))
        return flags
    
    # No futura (solo mes/año posteriores al actual; el día de pago del mes en curso es válido)
    now = datetime.now()
    if parsed.year > now.year or (parsed.year == now.year and parsed.month > now.month):
        flags.append(ValidationFlag("fecha_nomina", f"Fecha futura detectada: '{fecha}'", "error"))
    
    # No anterior a 2020
    if parsed.year < 2020:
        flags.append(ValidationFlag("fecha_nomina", f"Fecha muy antigua (antes de 2020): '{fecha}'", "warning"))
    
    return flags


def validate_nombre(nombre: Optional[str]) -> List[ValidationFlag]:
    """
    Valida el nombre del trabajador.
    
    Reglas:
    - No vacío
    - Al menos 2 palabras (nombre + apellido)
    - Sin caracteres numéricos (salvo DNI en el mismo campo, que filtramos)
    """
    flags = []
    
    if nombre is None or nombre.strip() == "":
        flags.append(ValidationFlag("nombre_trabajador", "Nombre no detectado", "error"))
        return flags
    
    clean = nombre.strip()
    
    # Al menos 2 palabras
    words = clean.split()
    if len(words) < 2:
        flags.append(ValidationFlag("nombre_trabajador", f"Nombre incompleto (solo {len(words)} palabra(s)): '{nombre}'", "warning"))
    
    # No debería contener números (a menos que sea DNI mezclado)
    if re.search(r'\d{3,}', clean):
        flags.append(ValidationFlag("nombre_trabajador", f"Nombre contiene secuencia numérica (posible DNI mezclado): '{nombre}'", "warning"))
    
    return flags


def validate_empresa(empresa: Optional[str]) -> List[ValidationFlag]:
    """
    Valida el nombre de la empresa.
    
    Reglas:
    - No vacío
    - Más de 2 caracteres
    - No debería ser solo números
    """
    flags = []
    
    if empresa is None or empresa.strip() == "":
        flags.append(ValidationFlag("nombre_empresa", "Empresa no detectada", "error"))
        return flags
    
    clean = empresa.strip()
    
    if len(clean) <= 2:
        flags.append(ValidationFlag("nombre_empresa", f"Nombre de empresa demasiado corto: '{empresa}'", "error"))
    
    if clean.isdigit():
        flags.append(ValidationFlag("nombre_empresa", f"Nombre de empresa solo contiene números: '{empresa}'", "error"))
    
    return flags


def validate_es_nomina(es_nomina: Optional[bool]) -> List[ValidationFlag]:
    """
    Valida que el documento procesado sea realmente una nómina.
    Este es el guardrail principal contra alucinaciones del LLM
    cuando se sube un documento que no es una nómina.
    """
    flags = []

    if es_nomina is None:
        flags.append(ValidationFlag(
            "es_nomina",
            "No se pudo determinar si el documento es una nómina. Revisar manualmente.",
            "warning"
        ))
    elif es_nomina is False:
        flags.append(ValidationFlag(
            "es_nomina",
            "El documento no parece ser una nómina española. No se deben confiar en los datos extraídos.",
            "error"
        ))

    return flags


def validate_extraction(extraction: NominaExtraction) -> Dict[str, Any]:
    """
    Función principal de validación.
    
    Recibe los datos extraídos por el LLM y devuelve:
    - validated_data: datos con campos corregidos si es posible
    - flags: lista de problemas detectados
    - overall_confidence: high | medium | low
    - status: validated | needs_review | error
    """
    all_flags: List[ValidationFlag] = []
    
    # Guardrail principal: ¿es realmente una nómina?
    all_flags.extend(validate_es_nomina(extraction.es_nomina))
    
    # Validar cada campo (solo si el documento parece una nómina)
    if extraction.es_nomina is not False:
        all_flags.extend(validate_iban(extraction.iban))
        all_flags.extend(validate_ingresos(extraction.ingresos_brutos, extraction.ingresos_netos))
        all_flags.extend(validate_fecha(extraction.fecha_nomina))
        all_flags.extend(validate_nombre(extraction.nombre_trabajador))
        all_flags.extend(validate_empresa(extraction.nombre_empresa))
    
    # Determinar confianza global
    errors = [f for f in all_flags if f.severity == "error"]
    warnings = [f for f in all_flags if f.severity == "warning"]
    
    if len(errors) > 0:
        overall_confidence = "low"
        status = "needs_review"
    elif len(warnings) > 0:
        overall_confidence = "medium"
        status = "validated"
    else:
        overall_confidence = "high"
        status = "validated"
    
    # Preparar respuesta
    result = {
        "validated_data": {
            "es_nomina": extraction.es_nomina,
            "nombre_trabajador": extraction.nombre_trabajador,
            "nombre_empresa": extraction.nombre_empresa,
            "ingresos_brutos": extraction.ingresos_brutos,
            "ingresos_netos": extraction.ingresos_netos,
            "fecha_nomina": extraction.fecha_nomina,
            "iban": extraction.iban,
        },
        "flags": [f.to_dict() for f in all_flags],
        "overall_confidence": overall_confidence,
        "status": status,
        "flag_count": {
            "errors": len(errors),
            "warnings": len(warnings),
            "total": len(all_flags)
        }
    }
    
    return result