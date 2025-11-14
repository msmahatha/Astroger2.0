
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.routes.api_routes import router as ai_router


app = FastAPI(title="Astrolozee AI Microservice")

@app.get("/")
async def root():
    return JSONResponse({"status": "ok", "message": "Astrolozee AI Service is running"})

@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy", "service": "astrolozee-ai"})

app.include_router(ai_router, prefix="/astro", tags=["AI"])



