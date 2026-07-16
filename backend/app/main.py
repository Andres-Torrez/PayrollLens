from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

load_dotenv()

# Importamos el router de upload
from app.routes import upload
from app.routes import extraction

# Crear carpeta uploads si no existe
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


app = FastAPI(
    title="NominaFlow API",
    description="Extracción inteligente de nóminas con OCR + LLM + validación",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoint de health ---
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "nominaflow",
        "version": "0.1.0"
    }

# --- Registrar el router de upload ---
# prefix="/api" → todas las rutas de upload tendrán /api/...
# tags=["upload"] → agrupa en la documentación de /docs
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(extraction.router, prefix="/api", tags=["extraction-validation"])


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)