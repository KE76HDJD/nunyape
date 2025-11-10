from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
from .models import PresentationCreate, PresentationResponse, SlideCreate, PresentationUpdate
from .orchestrator import PresentationOrchestrator, BatchOrchestrator

router = APIRouter()

@router.post("/presentations", response_model=PresentationResponse)
async def create_presentation(
    presentation_data: PresentationCreate,
    slides: List[SlideCreate],
    background_tasks: BackgroundTasks
):
    """Create a new presentation"""
    try:
        orchestrator = PresentationOrchestrator()
        presentation = await orchestrator.create_presentation(presentation_data, slides)
        return presentation
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/presentations/{presentation_id}", response_model=PresentationResponse)
async def get_presentation(presentation_id: str):
    """Get presentation by ID"""
    # Mock implementation
    from datetime import datetime
    return PresentationResponse(
        id=presentation_id,
        title="Sample Presentation",
        description="A sample presentation",
        status="published",
        theme="default",
        slides=[
            {
                "id": "slide_1",
                "title": "Introduction",
                "content": "Welcome to the presentation",
                "type": "title",
                "order": 1
            }
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        owner_id="user_123"
    )

@router.post("/presentations/batch", response_model=List[PresentationResponse])
async def create_presentations_batch(presentations_data: List[dict]):
    """Create multiple presentations in batch"""
    try:
        orchestrator = BatchOrchestrator()
        results = await orchestrator.create_multiple_presentations(presentations_data)
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/presentations/{presentation_id}", response_model=PresentationResponse)
async def update_presentation(presentation_id: str, update_data: PresentationUpdate):
    """Update presentation"""
    # Mock implementation
    from datetime import datetime
    return PresentationResponse(
        id=presentation_id,
        title=update_data.title or "Updated Presentation",
        description=update_data.description,
        status=update_data.status or "draft",
        theme=update_data.theme or "default",
        slides=[],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        owner_id="user_123"
    )

@router.delete("/presentations/{presentation_id}")
async def delete_presentation(presentation_id: str):
    """Delete presentation"""
    return {"message": f"Presentation {presentation_id} deleted successfully"}