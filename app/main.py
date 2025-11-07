from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import edison

app = FastAPI(
    title="My FastAPI App", description="A sample FastAPI application", version="1.0.0"
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
app.include_router(edison.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI!"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
