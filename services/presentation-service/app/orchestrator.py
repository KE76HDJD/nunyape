import asyncio
from typing import List, Dict, Any
from datetime import datetime
from .models import PresentationCreate, SlideCreate, PresentationResponse

class PresentationOrchestrator:
    def __init__(self):
        self.processing_pipeline = [
            self._validate_input,
            self._create_presentation_structure,
            self._generate_slides,
            self._apply_theme,
            self._finalize_presentation
        ]
    
    async def create_presentation(self, presentation_data: PresentationCreate, 
                                slides_data: List[SlideCreate]) -> PresentationResponse:
        """Orchestrate the presentation creation process"""
        try:
            context = {
                'presentation_data': presentation_data,
                'slides_data': slides_data,
                'processing_steps': []
            }
            
            # Execute processing pipeline
            for step in self.processing_pipeline:
                context = await step(context)
            
            return context['final_presentation']
            
        except Exception as e:
            raise Exception(f"Presentation creation failed: {str(e)}")
    
    async def _validate_input(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data"""
        presentation_data = context['presentation_data']
        slides_data = context['slides_data']
        
        if not presentation_data.title.strip():
            raise ValueError("Presentation title cannot be empty")
        
        if len(slides_data) == 0:
            raise ValueError("Presentation must have at least one slide")
        
        context['processing_steps'].append('input_validated')
        return context
    
    async def _create_presentation_structure(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create presentation structure"""
        # Simulate structure creation
        await asyncio.sleep(0.1)
        context['structure'] = {
            'total_slides': len(context['slides_data']),
            'slide_types': list(set(slide.slide_type for slide in context['slides_data']))
        }
        context['processing_steps'].append('structure_created')
        return context
    
    async def _generate_slides(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate slides content"""
        slides = []
        for i, slide_data in enumerate(context['slides_data']):
            slide = {
                'id': f"slide_{i+1}",
                'title': slide_data.title,
                'content': slide_data.content,
                'type': slide_data.slide_type,
                'order': slide_data.order,
                'metadata': slide_data.metadata
            }
            slides.append(slide)
            # Simulate processing time per slide
            await asyncio.sleep(0.05)
        
        context['slides'] = slides
        context['processing_steps'].append('slides_generated')
        return context
    
    async def _apply_theme(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply theme to presentation"""
        theme = context['presentation_data'].theme
        # Simulate theme application
        await asyncio.sleep(0.1)
        context['theme_applied'] = theme
        context['processing_steps'].append('theme_applied')
        return context
    
    async def _finalize_presentation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Finalize presentation creation"""
        presentation_data = context['presentation_data']
        
        final_presentation = PresentationResponse(
            id=f"pres_{int(datetime.utcnow().timestamp())}",
            title=presentation_data.title,
            description=presentation_data.description,
            status="draft",
            theme=context['theme_applied'],
            slides=context['slides'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            owner_id="user_123"  # In real app, this would come from auth
        )
        
        context['final_presentation'] = final_presentation
        context['processing_steps'].append('finalized')
        return context

class BatchOrchestrator:
    def __init__(self):
        self.presentation_orchestrator = PresentationOrchestrator()
    
    async def create_multiple_presentations(self, 
                                          presentations_data: List[Dict[str, Any]]) -> List[PresentationResponse]:
        """Create multiple presentations in batch"""
        tasks = []
        for data in presentations_data:
            presentation_data = PresentationCreate(**data['presentation'])
            slides_data = [SlideCreate(**slide) for slide in data['slides']]
            task = self.presentation_orchestrator.create_presentation(presentation_data, slides_data)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [result for result in results if not isinstance(result, Exception)]