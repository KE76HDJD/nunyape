from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager
from app.routes import router as webhook_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webhook_service.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('webhook-service')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Webhook Service...")
    
    # Initialize connections, load configuration, etc.
    await initialize_service()
    
    yield
    
    # Shutdown
    logger.info("Shutting down Webhook Service...")
    await cleanup_service()

app = FastAPI(
    title="Webhook Service API",
    description="Centralized webhook handling service for multiple providers",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(webhook_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Webhook Service API",
        "version": "1.0.0",
        "description": "Centralized webhook handling for Stripe, PayPal, MIN, and custom providers"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "webhook-service",
        "timestamp": "2024-01-01T00:00:00Z"  # In real app, use current time
    }

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    # Check dependencies (database, message queue, etc.)
    dependencies_ready = await check_dependencies()
    
    if dependencies_ready:
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

async def initialize_service():
    """Initialize service components"""
    logger.info("Initializing webhook service components...")
    
    # Initialize database connection
    # Initialize message queue
    # Load configuration
    # Setup background tasks
    
    logger.info("Webhook service initialization complete")

async def cleanup_service():
    """Cleanup service components"""
    logger.info("Cleaning up webhook service...")
    
    # Close database connections
    # Stop background tasks
    # Cleanup resources
    
    logger.info("Webhook service cleanup complete")

async def check_dependencies() -> bool:
    """Check if all dependencies are ready"""
    try:
        # Check database connection
        # Check message queue connection
        # Check external service availability
        
        return True  # Simplified for example
        
    except Exception as e:
        logger.error(f"Dependency check failed: {e}")
        return False

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8090,
        log_level="info",
        access_log=True
    )