from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.generate import router as generate_router
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Cofoundr AI - Pitch Deck Generator",
    description="AI-powered startup pitch deck generation service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generate_router, prefix="/api", tags=["Pitch Generation"])

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Cofoundr AI Pitch Deck Generator",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "generate_pitch": "/api/generate",
            "generate_detailed_pitch": "/api/generate-detailed",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    """Global health check endpoint."""
    api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
    mock_mode = os.getenv("MOCK_MODE", "false").lower() == "true"
    return {
        "status": "healthy",
        "service": "cofoundr-ai-server",
        "openai_configured": api_key_configured,
        "mock_mode": mock_mode
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
