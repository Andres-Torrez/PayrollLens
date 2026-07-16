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
- nombre_trabajador: nombre completo del empleado
- nombre_empresa: nombre de la empresa o razón social
- ingresos_brutos: TOTAL DEVENGOS / BRUTO (solo número, sin símbolos de moneda ni puntos de miles)
- ingresos_netos: LÍQUIDO A PERCIBIR / NETO (solo número, sin símbolos de moneda). Suele estar en la segunda página.
- fecha_nomina: período de la nómina (formato: MM/YYYY o DD/MM/YYYY)
- iban: número de cuenta bancaria IBAN completo (debe empezar por ES y tener 24 caracteres, sin espacios). Suele estar en "DATOS BANCARIOS".

REGLAS ESTRICTAS:
1. Devuelve ÚNICAMENTE un objeto JSON válido. Sin texto explicativo antes ni después.
2. Si un campo no está visible o es ilegible, usa null.
3. Los ingresos deben ser números (float), sin símbolos €. Ejemplo: 2450.67
4. El IBAN debe tener exactamente 24 caracteres y empezar por ES (quita espacios).
5. Si detectas que algún campo es dudoso, borroso o incierto, usa "confidence": "low".
   Si todo está claro, usa "confidence": "high".

Formato obligatorio (solo este JSON, nada más):
{
  "nombre_trabajador": "string o null",
  "nombre_empresa": "string o null",
  "ingresos_brutos": number o null,
  "ingresos_netos": number o null,
  "fecha_nomina": "string o null",
  "iban": "string o null",
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

        extraction = NominaExtraction(
            nombre_trabajador=data.get("nombre_trabajador"),
            nombre_empresa=data.get("nombre_empresa"),
            ingresos_brutos=data.get("ingresos_brutos"),
            ingresos_netos=data.get("ingresos_netos"),
            fecha_nomina=data.get("fecha_nomina"),
            iban=data.get("iban"),
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
