from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes, public, challenges, submission, user, admin
from .database import get_db

app = FastAPI(title="CordonCTF", version="1.0.0")

# CORS – allow all origins for local hotspot usage
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(auth_routes.router)
app.include_router(public.router)
app.include_router(challenges.router)
app.include_router(submission.router)
app.include_router(user.router)
app.include_router(admin.router)

# Serve frontend static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Serve uploaded challenge files (optional but convenient)
import os
from .config import UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/test-db")
def test_db(cursor=Depends(get_db)):
    cursor.execute("SELECT 1")
    return {"database": "connected"}