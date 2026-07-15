# NominaAI

Extractor inteligente de nóminas con OCR + LLM + validación de datos.

&gt; Challenge técnico para Kontaktu AI — Julio 2026

## Visión

Una web app donde subes una nómina (PDF o imagen) y la IA extrae:
- Nombre del trabajador
- Ingresos brutos y netos
- Nombre de la empresa
- Fecha del documento
- IBAN

Lo interesante: **la IA a veces falla**, y nosotros detectamos, verificamos y corregimos.

## Stack

- **Backend:** Python + FastAPI
- **Frontend:** Next.js 14 + Tailwind + shadcn/ui
- **OCR/IA:** Groq (Llama 4 Scout)
- **Base de datos:** SQLite
- **IDE:** Cursor
- **Asistente IA:** Kimi Claw

## Estado

En desarrollo — Tarea 1: Setup inicial
