# backend/main.py
from fastapi import FastAPI, Depends
from .database import get_db

app = FastAPI()

@app.get("/api/health")
def health():
    return {"status": "ok"}

# Temporary DB connection test endpoint
@app.get("/api/test-db")
def test_db(cursor=Depends(get_db)):
    cursor.execute("SELECT 1 AS test")
    result = cursor.fetchone()
    return {"db_test": result}