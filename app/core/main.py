from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routes import tasks

app = FastAPI(
    title="FastAPI CPU-Heavy Task POC",
    description="Proof of Concept for optimizing CPU-intensive operations in FastAPI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include task routes
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])

@app.get("/")
async def root():
    """Root endpoint for CPU-heavy task POC."""
    return {
        "message": "FastAPI CPU-Heavy Task POC",
        "description": "Test different approaches for handling CPU-intensive operations",
        "endpoints": {
            "docs": "/docs",
            "tasks": "/api/v1/tasks"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True) 