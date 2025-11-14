
from fastapi import FastAPI
from src.routes.api_routes import router as ai_router


app = FastAPI(title="Astrolozee AI Microservice")

app.include_router(ai_router, prefix="/astro", tags=["AI"])



