from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routes import router as qa_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(
    title="Q&A Service API",
    description="Question Answering service with knowledge base",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(qa_router, prefix="/api/v1/qa")

@app.get("/")
async def root():
    return {"message": "Q&A Service API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "qa-service"}

@app.get("/ready")
async def readiness_check():
    # Check if knowledge base is accessible
    try:
        from app.knowledge_base import KnowledgeBase
        kb = KnowledgeBase()
        # Simple query to test database
        kb.search_documents("test", limit=1)
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}, 503

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)