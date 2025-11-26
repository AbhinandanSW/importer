from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import products, upload, webhooks

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="CSV Product Importer API",port=10000,host="0.0.0.0")

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

