"""FastAPI application for ARRS web interface."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from arrs.api.routes import router as api_router

app = FastAPI(
    title="ARRS - AI Readability & Recommendation Score",
    description="Optimize for AI citations, not search rankings",
    version="1.0.0"
)

# Mount API routes
app.include_router(api_router, prefix="/api")

# Serve static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Serve the main HTML page."""
    return FileResponse(str(static_dir / "index.html"))


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "message": "ARRS API is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
