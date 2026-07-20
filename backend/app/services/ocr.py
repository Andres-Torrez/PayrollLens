import base64
import json
import os
from pathlib import Path
from typing import List, Tuple

import fitz  # pymupdf
from dotenv import load_dotenv
from openai import OpenAI

from app.models.schemas import NominaExtraction

load_dotenv()

# Cliente GitHub Models (OpenAI-compatible)
client = OpenAI(
    base_url="https://models.github.ai/inference",
    api_key=os.getenv("GITHUB_TOKEN"),
)

MAX_PDF_PAGES = 3


def file_to_images(file_path: str) -> List[Tuple[str, str]]:
    """
    Convierte un archivo a una o más imágenes base64.
    PDFs: todas las páginas (hasta MAX_PDF_PAGES).
    Imágenes: una sola.

    Returns:
        Lista de (base64_string, mime_type)
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        doc = fitz.open(file_path)
        images: List[Tuple[str, str]] = []
        for page_index in range(min(doc.page_count, MAX_PDF_PAGES)):
            page = doc[page_index]
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            images.append((base64.b64encode(img_bytes).decode("utf-8"), "image/png"))
        doc.close()
        return images

    with open(file_path, "rb") as f:
        img_bytes = f.read()
    mime = f"image/{suffix.replace('.', '')}"
    if mime == "image/jpg":
        mime = "image/jpeg"
    return [(base64.b64encode(img_bytes).decode("utf-8"), mime)]


def extract_from_file(file_path: str) -> Tuple[NominaExtraction, str]:
    images = file_to_images(file_path)

    prompt = """Eres un extractor experto de documentos de nóminas españolas.

Analiza TODAS las páginas de la imagen de esta nómina y extrae los siguientes campos EXACTOS:
- nombre_trabajador: nombre completo de la PERSONA física empleada (nunca una razón social)
- nombre_empresa: razón social de la EMPRESA pagadora (nunca el nombre de una persona)
- ingresos_brutos: TOTAL DEVENGOS / BRUTO del PERÍODO DE LIQUIDACIÓN (mensual). Solo número.
- ingresos_netos: LÍQUIDO A PERCIBIR / NETO del mismo período (mensual). Solo número. Suele estar en la 2ª página.
- fecha_nomina: período de liquidación (preferir MM/YYYY, ej. 07/2026). NO uses la fecha de pago.
- iban: IBAN completo (debe empezar por ES y tener 24 caracteres, sin espacios). Suele estar en "DATOS BANCARIOS".
- anomalias: lista de códigos de problemas del documento (puede ser []). Obligatorio informarlos aunque corrijas los valores.

REGLAS ESTRICTAS:
1. Devuelve ÚNICAMENTE un objeto JSON válido. Sin texto explicativo antes ni después.
2. Primero decide si el documento ES UNA NÓMINA ESPAÑOLA. Usa "es_nomina": true solo si ves conceptos propios de nómina (devengos, liquidación, IRPF, SS, líquido a percibir, etc.). Si es otra cosa (factura, DNI, contrato, recibo genérico), usa "es_nomina": false.
3. Si "es_nomina" es false, el resto de campos pueden ser null y anomalias=[].
4. Si un campo no está visible o es ilegible, usa null.
5. Los ingresos deben ser números (float), sin símbolos € ni puntos de miles. Ejemplo: 2450.67
6. El IBAN debe tener exactamente 24 caracteres y empezar por ES (quita espacios).
7. Si hay CUALQUIER anomalía o corrección, "confidence" DEBE ser "low". Solo "high" si el documento es claro y sin anomalías.

IMPORTES (mensual vs anual) — CRÍTICO:
8. Los ingresos_brutos e ingresos_netos DEBEN corresponder al período de liquidación mensual, NO al total anual.
9. Si ves etiquetas como "TOTAL DEVENGOS ANUALES", "LÍQUIDO A PERCIBIR ANUAL", "remuneración anual" o notas que digan que el importe se divide en N pagas:
   - NO uses esos totales anuales como ingresos_*.
   - Si tomas el mensual de una nota/advertencia, rellena ingresos_* con el mensual Y añade a anomalias: "importes_anuales_en_documento".
10. Si solo ves cifras anuales (p. ej. 100.000+) y NO encuentras el mensual, usa null en ingresos_* , anomalias: ["importes_anuales_en_documento"] y confidence "low".

EMPRESA vs TRABAJADOR — CRÍTICO:
11. NO copies a ciegas lo que hay junto a las etiquetas si el contenido no encaja semánticamente.
12. nombre_trabajador debe ser una persona (nombre + apellidos). NUNCA formas societarias (S.L., S.A., S.L.U., S.C., C.B., etc.).
13. nombre_empresa debe ser una razón social (suele incluir S.L./S.A./etc.).
14. Si las etiquetas están cruzadas (p. ej. "Nombre y Apellidos" tiene una S.L. y "Razón Social" tiene nombre de persona): CORRIGE el cruce en los campos Y añade a anomalias: "etiquetas_empresa_trabajador_cruzadas". confidence "low".
15. Pistas: CIF tipo B-######## / A-######## → empresa; DNI tipo 12345678A → persona.

Códigos válidos en anomalias (usa exactamente estos strings):
- "importes_anuales_en_documento"
- "etiquetas_empresa_trabajador_cruzadas"

Formato obligatorio (solo este JSON, nada más):
{
    "es_nomina": true | false,
    "nombre_trabajador": "string o null",
    "nombre_empresa": "string o null",
    "ingresos_brutos": number o null,
    "ingresos_netos": number o null,
    "fecha_nomina": "string o null",
    "iban": "string o null",
    "anomalias": [],
    "confidence": "high" | "low"
}"""

    content = [{"type": "text", "text": prompt}]
    for base64_image, mime_type in images:
        content.append(
            {
                "type": "image_url",
                "image_url": {"url": f"data:{mime_type};base64,{base64_image}"},
            }
        )

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": content}],
            temperature=0.1,
            max_tokens=1024,
        )

        raw_response = response.choices[0].message.content
        print(f"[OCR] Raw response ({len(images)} page(s)):\n{raw_response}\n")

    except Exception as e:
        print(f"[OCR] Error: {e}")
        return NominaExtraction(
            confidence="low",
            raw_llm_response=f"ERROR: {str(e)}",
        ), f"ERROR: {str(e)}"

    try:
        text = raw_response.strip()

        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_str = text.split("```")[1].split("```")[0].strip()
        else:
            json_str = text

        data = json.loads(json_str)

        anomalias_raw = data.get("anomalias") or []
        if not isinstance(anomalias_raw, list):
            anomalias_raw = []

        extraction = NominaExtraction(
            es_nomina=data.get("es_nomina"),
            nombre_trabajador=data.get("nombre_trabajador"),
            nombre_empresa=data.get("nombre_empresa"),
            ingresos_brutos=data.get("ingresos_brutos"),
            ingresos_netos=data.get("ingresos_netos"),
            fecha_nomina=data.get("fecha_nomina"),
            iban=data.get("iban"),
            anomalias=[str(a) for a in anomalias_raw],
            confidence=data.get("confidence", "high"),
            raw_llm_response=raw_response,
        )

        return extraction, raw_response

    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[OCR] JSON parsing failed: {e}")
        return NominaExtraction(
            confidence="low",
            raw_llm_response=raw_response,
        ), raw_response
