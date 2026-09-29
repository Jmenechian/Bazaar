import logging
import os
from dotenv import load_dotenv

# Load local environment variables from .env file
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from router.router import router
from utils import api_setup

logging.basicConfig(level=logging.INFO)

# Run OpenAPI customization
api_setup()

app = FastAPI(
    title="Bazaar Users & Authentication Service",
    description="Manages user accounts, authentication, and profiles for the Bazaar platform.",
    version="1.0.0",
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes with /api/v1 prefix and also top-level for convenience
app.include_router(router, prefix="/api/v1")
app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "Bazaar Users Service",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
