import sqlite3
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from render_report import generate_pdf

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


def create_reports_table():
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()


create_reports_table()


@app.post("/reports", status_code=201)
def create_report():
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()

    created_at = datetime.now().isoformat()

    cursor.execute(
        "INSERT INTO reports (path, created_at) VALUES (?, ?)",
        ("", created_at)
    )

    report_id = cursor.lastrowid
    path = f"reports/{report_id}.pdf"

    cursor.execute(
        "UPDATE reports SET path = ? WHERE id = ?",
        (path, report_id)
    )

    conn.commit()
    conn.close()

    generate_pdf(path)

    return {
        "id": report_id,
        "file": f"/reports/{report_id}/file"
    }


@app.get("/reports/{report_id}")
def get_report(report_id: int):
    conn = sqlite3.connect("report.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, path, created_at FROM reports WHERE id = ?",
        (report_id,)
    )

    report = cursor.fetchone()
    conn.close()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    return {
        "id": report["id"],
        "path": report["path"],
        "created_at": report["created_at"],
        "file": f"/reports/{report_id}/file"
    }


@app.get("/reports/{report_id}/file")
def download_report(report_id: int):
    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT path FROM reports WHERE id = ?",
        (report_id,)
    )

    report = cursor.fetchone()
    conn.close()

    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    path = report[0]

    if not Path(path).exists():
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"report-{report_id}.pdf"
    )