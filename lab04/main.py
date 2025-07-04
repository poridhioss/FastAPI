from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes import auth, users

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="JWT Authentication API",
    description="A simple JWT authentication API with FastAPI and PostgreSQL",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(users.router)


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "JWT Authentication API",
        "version": "1.0.0",
        "endpoints": {
            "signup": "/auth/signup",
            "login": "/auth/login",
            "profile": "/users/profile",
            "docs": "/docs"
        }
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}