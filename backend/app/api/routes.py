from fastapi import APIRouter
from app.api.research_routes import router as research_router
from app.api.websocket import ws_router

api_router = APIRouter()

# Health check
@api_router.get("/health", tags=["Health"])
async def health_check():
    """Service health verification endpoint."""
    return {
        "status": "healthy",
        "service": "research-agent-backend",
        "version": "1.0.0",
    }

# Mount sub-routers
api_router.include_router(research_router)
