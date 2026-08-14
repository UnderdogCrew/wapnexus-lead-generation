import asyncio

from fastapi import APIRouter, HTTPException

from app.schemas import PipelineRunRequest, PipelineRunResponse
from app.services.pipeline import persist_leads, run_pipeline

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
async def run_lead_pipeline(body: PipelineRunRequest):
    """Scrape → classify → extract pain points → generate outreach drafts."""
    try:
        # Scraping + LLM calls are sync/blocking; run off the event loop.
        leads = await asyncio.to_thread(
            run_pipeline,
            body.category,
            body.city,
            body.min_fit_score,
            body.max_pages,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Pipeline failed: {e}") from e

    if body.persist:
        await persist_leads(leads, min_fit_score=body.min_fit_score)

    qualified = [lead for lead in leads if (lead.get("fit_score") or 0) >= body.min_fit_score]
    return PipelineRunResponse(
        category=body.category,
        city=body.city,
        total_leads=len(leads),
        qualified_leads=len(qualified),
        leads=leads,
    )
