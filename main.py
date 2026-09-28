import sqlite3
from datetime import datetime, date
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel

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


class ReportRequest(BaseModel):
    force: bool = False


@app.post("/reports")
def create_report(
    response: Response,
    request: ReportRequest | None = None
):
    force = request.force if request else False

    conn = sqlite3.connect("report.db")
    cursor = conn.cursor()

    today = date.today().isoformat()

    # Check whether a report was already created today
    if not force:
        cursor.execute("""
            SELECT id, path
            FROM reports
            WHERE substr(created_at, 1, 10) = ?
            ORDER BY id DESC
            LIMIT 1
        """, (today,))

        existing_report = cursor.fetchone()

        if existing_report:
            report_id = existing_report[0]

            conn.close()

            response.status_code = 200

            return {
                "id": report_id,
                "file": f"/reports/{report_id}/file"
            }

    # Create a new report
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

    response.status_code = 201

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
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

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
        raise HTTPException(
            status_code=404,
            detail="Report not found"
        )

    path = report[0]

    if not Path(path).exists():
        raise HTTPException(
            status_code=404,
            detail="PDF file not found"
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=f"report-{report_id}.pdf"
    )