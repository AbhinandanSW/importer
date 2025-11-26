from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import aiohttp
import os
from .database import engine, Base
from .routers import products, upload, webhooks

# Create database tables
Base.metadata.create_all(bind=engine)


async def keep_alive_task():
    """Background task to ping health check endpoint to keep server alive"""
    await asyncio.sleep(30)  # Wait 30 seconds after startup
    
    # Get the server URL from environment or use default
    server_url = os.getenv("RENDER_SERVICE_URL", os.getenv("SERVER_URL", "http://localhost:10000"))
    health_url = f"{server_url}/health"
    
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                    # Just ping, don't need to check response
                    pass
        except Exception:
            # Silently fail - server might be starting up
            pass
        
        # Ping every 10 minutes (600 seconds) to keep server alive
        # Render spins down after 15 minutes of inactivity
        await asyncio.sleep(600)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup: Start keep-alive task
    keep_alive = asyncio.create_task(keep_alive_task())
    yield
    # Shutdown: Cancel keep-alive task
    keep_alive.cancel()
    try:
        await keep_alive
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="CSV Product Importer API",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products.router, prefix="/api/products", tags=["products"])
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])


@app.get("/")
def root():
    return {"message": "CSV Product Importer API"}


@app.get("/health")
def health_check():
    """Health check endpoint for Render and monitoring services"""
    return {
        "status": "healthy",
        "service": "CSV Product Importer API"
    }

