import sqlite3

from fastapi import FastAPI
from fastapi.responses import FileResponse

DB_PATH = "tv.db"

app = FastAPI()


def query_db(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(sql, params).fetchall()
    finally:
        conn.close()
    return [dict(row) for row in rows]


@app.get("/")
def home():
    return FileResponse("index.html")


@app.get("/api/categories")
def categories():
    rows = query_db("""
        SELECT DISTINCT channels.category
        FROM channels
        JOIN streams ON streams.channel_id = channels.id
        WHERE streams.status = 'working' AND channels.category != ''
        ORDER BY channels.category
    """)
    return [row["category"] for row in rows]


@app.get("/api/channels")
def channels(category: str = "", search: str = ""):
    sql = """
        SELECT channels.id, channels.name, channels.logo,
               channels.category, streams.url
        FROM streams
        JOIN channels ON channels.id = streams.channel_id
        WHERE streams.status = 'working'
    """
    params = []

    if category:
        sql += " AND channels.category = ?"
        params.append(category)

    if search:
        sql += " AND channels.name LIKE ?"
        params.append(f"%{search}%")

    sql += " ORDER BY channels.name"
    return query_db(sql, params)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
