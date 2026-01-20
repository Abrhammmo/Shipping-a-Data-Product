from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from api.database import get_db
from api import schemas

app = FastAPI(
    title="Medical Telegram Analytics API",
    description="Analytical API exposing insights from the Medical Telegram Data Warehouse",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Welcome to the Medical Telegram Analytics API. Visit /docs for API documentation."}

@app.get(
    "/api/reports/top-products",
    response_model=list[schemas.TopProduct],
    summary="Top mentioned products across all channels"
)
def top_products(limit: int = Query(10, ge=1), db: Session = Depends(get_db)):
    query = text("""
        SELECT term, COUNT(*) AS frequency
        FROM marts.fct_message_terms
        GROUP BY term
        ORDER BY frequency DESC
        LIMIT :limit
    """)

    results = db.execute(query, {"limit": limit}).fetchall()
    return [{"term": r.term, "frequency": r.frequency} for r in results]
@app.get(
    "/api/channels/{channel_key}/activity",
    response_model=list[schemas.ChannelActivity],
    summary="Posting activity over time for a channel"
)
def channel_activity(channel_key: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT d.date, COUNT(*) AS message_count
        FROM marts.fct_messages f
        JOIN marts.dim_date d ON f.date_key = d.date_key
        WHERE f.channel_key = :channel_key
        GROUP BY d.date
        ORDER BY d.date
    """)

    results = db.execute(query, {"channel_key": channel_key}).fetchall()

    if not results:
        raise HTTPException(status_code=404, detail="Channel not found")

    return [{"date": r.date, "message_count": r.message_count} for r in results]
@app.get(
    "/api/search/messages",
    response_model=list[schemas.MessageSearchResult],
    summary="Search messages by keyword"
)
def search_messages(
    query: str,
    limit: int = Query(20, ge=1),
    db: Session = Depends(get_db)
):
    sql = text("""
        SELECT message_id, channel_key, message_text, message_date
        FROM marts.fct_messages
        WHERE message_text ILIKE :pattern
        ORDER BY message_date DESC
        LIMIT :limit
    """)

    results = db.execute(
        sql,
        {"pattern": f"%{query}%", "limit": limit}
    ).fetchall()

    return [
        {
            "message_id": r.message_id,
            "channel_key": r.channel_key,
            "message_text": r.message_text,
            "date": r.message_date
        }
        for r in results
    ]
@app.get(
    "/api/reports/visual-content",
    response_model=list[schemas.VisualContentStat],
    summary="Image usage statistics across channels"
)
def visual_content_stats(db: Session = Depends(get_db)):
    query = text("""
        SELECT
            channel_key,
            COUNT(*) AS image_count,
            COUNT(*) FILTER (WHERE image_category = 'promotional') AS promotional_count
        FROM marts.fct_image_detections
        GROUP BY channel_key
        ORDER BY image_count DESC
    """)

    results = db.execute(query).fetchall()

    return [
        {
            "channel_key": r.channel_key,
            "image_count": r.image_count,
            "promotional_count": r.promotional_count
        }
        for r in results
    ]
