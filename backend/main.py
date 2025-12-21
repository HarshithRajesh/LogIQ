from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import psycopg2
from psycopg2.extras import execute_values
import uvicorn
import sys

app = FastAPI()

# --- CONFIGURATION ---
DB_CONFIG = {
    "host": "localhost",
    "database": "logiq",
    "user": "admin",
    "password": "password"
}

# --- DATA MODEL ---
class LogItem(BaseModel):
    content: str
    template: str

# --- UTILITY: Get DB Connection ---
def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        print(f"❌ DB CONNECTION ERROR: {e}")
        return None

# --- HEALTH CHECK (Open http://localhost:8000 in browser) ---
@app.get("/")
def health_check():
    conn = get_db_connection()
    if conn:
        conn.close()
        return {"status": "Online", "database": "Connected ✅"}
    return {"status": "Online", "database": "Disconnected ❌ (Check Docker)"}

# --- INGESTION API ---
@app.post("/ingest")
def ingest_logs(logs: List[LogItem]):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database Unavailable")
    
    cursor = conn.cursor()
    
    # Efficient Bulk Insert
    query = "INSERT INTO logs (log_template, raw_content) VALUES %s"
    data_tuples = [(log.template, log.content) for log in logs]
    
    try:
        execute_values(cursor, query, data_tuples)
        conn.commit()
        print(f"✅ Inserted {len(logs)} logs.")
    except Exception as e:
        conn.rollback()
        print(f"⚠️ INSERT ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
        
    return {"status": "received", "count": len(logs)}

if __name__ == "__main__":
    print("🚀 Starting Backend on http://0.0.0.0:8000")
    # Using reload=True helps see errors immediately
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
