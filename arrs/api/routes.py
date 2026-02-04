"""FastAPI routes for ARRS web interface."""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional
import asyncio

from arrs.storage.database import Database
from arrs.storage.json_store import JSONStore
from arrs.storage.repository import Repository
from arrs.core.orchestrator import AnalysisOrchestrator
from arrs.reporting.report_generator import ReportGenerator
from config import settings

router = APIRouter()

# Global instances
db_path = settings.database_url.replace("sqlite:///", "")
db = Database(db_path)
json_store = JSONStore(settings.json_storage_path)
repository = Repository(db, json_store)


class AnalyzeRequest(BaseModel):
    """Request model for analysis."""
    url: HttpUrl
    brand: Optional[str] = None
    category: Optional[str] = None
    use_case: Optional[str] = None


class AnalyzeResponse(BaseModel):
    """Response model for analysis."""
    analysis_id: str
    status: str
    message: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_url(request: AnalyzeRequest, background_tasks: BackgroundTasks):
    """
    Analyze a URL and return analysis ID.

    The analysis runs in the background. Use /analysis/{id} to check status.
    """
    orchestrator = AnalysisOrchestrator(repository)

    # Convert HttpUrl to string
    url_str = str(request.url)

    try:
        # Run analysis in background
        analysis_id = await orchestrator.analyze_url(
            url_str,
            brand=request.brand,
            product_category=request.category,
            use_case=request.use_case
        )

        return AnalyzeResponse(
            analysis_id=analysis_id,
            status="completed",
            message=f"Analysis completed successfully"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID."""
    try:
        orchestrator = AnalysisOrchestrator(repository)
        summary = await orchestrator.get_analysis_summary(analysis_id)

        if not summary:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return JSONResponse(content=summary)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/{analysis_id}")
async def get_report(analysis_id: str):
    """Get detailed report by analysis ID."""
    try:
        report_gen = ReportGenerator(repository)
        report = await report_gen.generate_report(analysis_id)

        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return JSONResponse(content=report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "llm_provider": settings.llm_provider,
        "engines": ["ADE", "ARCE", "TRE"]
    }
