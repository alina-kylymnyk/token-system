from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.cache import cache
from app.db.database import engine, Base

# Import routers
from app.api.internal import router as internal_router
from app.api.v1 import router as v1_router
from app.api.admin import router as admin_router


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    docs_url="/docs",
    redoc_url="/redoc",
    description="Credits System API with subscription management"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(internal_router, prefix="/api/internal")
app.include_router(v1_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/admin")

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print(f"\n{'='*60}")
    print(f"Starting {settings.APP_NAME}")
    print(f"Version: {settings.API_VERSION}")
    print(f"{'='*60}")

    # Create database tables (for development)
    if settings.DEBUG:
        print("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Database tables created")

    # Check Redis connection
    if cache.ping():
        print(" Redis connected")
    else:
        print(" Redis connection failed")

    print(f"\nAPI Documentation:")
    print(f"  Swagger UI: http://localhost:8000/docs")
    print(f"  ReDoc: http://localhost:8000/redoc")
    print(f"{'='*60}\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print(f"Shutting down {settings.APP_NAME}...")

@app.get("/")
async def root():
     """Health check endpoint"""
     return{
        "app": settings.APP_NAME,
        "version": settings.API_VERSION,
        "status": "healthy",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
     """Detailed health check"""
     return {
        "app": settings.APP_NAME,
        "database": "connected",
        "redis": "connected" if cache.ping() else "disconnected",
        "endpoints": {
            "internal": "/api/internal",
            "public": "/api/v1",
            "admin": "/api/admin"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )