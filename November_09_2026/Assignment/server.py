from fastapi import FastAPI, HTTPException, status
from database import get_db_connection
import psycopg2

app = FastAPI()

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    conn = None
    cur = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()

        if result:
            return {
                "status": "healthy",
                "database": "connected"
            }

    except psycopg2.Error as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()