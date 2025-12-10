from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(title="LogIQ API", version="1.0.0")

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "admin",
    "password": "admin",
    "database": "logiq"
}

# Pydantic Models
class LogEntry(BaseModel):
    timestamp: datetime
    service_name: str
    severity: str
    template_id: Optional[str] = None
    log_template: Optional[str] = None
    parameters: Optional[List[str]] = None
    raw_message: str

    class Config:
        json_schema_extra = {
            "example": {
                "timestamp": "2024-12-10T10:30:00",
                "service_name": "auth-service",
                "severity": "INFO",
                "template_id": "AUTH_001",
                "log_template": "User {} logged in from IP {}",
                "parameters": ["john_doe", "192.168.1.1"],
                "raw_message": "User john_doe logged in from IP 192.168.1.1"
            }
        }


def get_db_connection():
    """Create and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "healthy", "service": "LogIQ API"}


@app.get("/health")
async def health_check():
    """Check database connectivity."""
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/ingest", status_code=201)
async def ingest_logs(logs: List[LogEntry]):
    """
    Ingest a batch of log entries into the database.
    Uses execute_values for high-speed batch insertion.
    """
    if not logs:
        raise HTTPException(status_code=400, detail="No logs provided")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Prepare data for bulk insertion
        # Important: Convert None parameters to empty list []
        values = [
            (
                log.timestamp,
                log.service_name,
                log.severity,
                log.template_id,
                log.log_template,
                log.parameters if log.parameters is not None else [],  # Convert None to empty list
                log.raw_message
            )
            for log in logs
        ]
        
        # SQL query for insertion
        insert_query = """
            INSERT INTO logs 
            (timestamp, service_name, severity, template_id, log_template, parameters, raw_message)
            VALUES %s
        """
        
        # High-speed batch insertion using execute_values
        execute_values(
            cursor,
            insert_query,
            values,
            template="(%s, %s, %s, %s, %s, %s, %s)",
            page_size=1000  # Process in chunks of 1000
        )
        
        conn.commit()
        cursor.close()
        
        logger.info(f"Successfully ingested {len(logs)} log entries")
        
        return {
            "status": "success",
            "message": f"Ingested {len(logs)} log entries",
            "count": len(logs)
        }
        
    except psycopg2.Error as e:
        if conn:
            conn.rollback()
        logger.error(f"Database error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Unexpected error during ingestion: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    
    finally:
        if conn:
            conn.close()


@app.get("/logs/count")
async def get_log_count():
    """Get the total count of logs in the database."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM logs")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return {"total_logs": count}
        
    except Exception as e:
        logger.error(f"Error fetching log count: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
