# PDF Report Generator

A FastAPI backend that reads scraped book data from SQLite, uses SQL aggregation to create report statistics, renders the data as HTML, and generates a downloadable PDF using Playwright.

## Dataset

This project reuses the 60 validated book records collected from Books to Scrape in my previous polite scraper assignment.

Each book contains:

- title
- price
- rating
- URL

## Tech Stack

- Python
- FastAPI
- SQLite
- Playwright
- Chromium

## Setup

Create and activate a virtual environment:

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Install Chromium for Playwright:

```bash
playwright install chromium
```

## Seed the Database

Run:

```bash
python seed.py
```

Expected result:

```text
Books in database: 60
```

Running the seed script multiple times still leaves exactly 60 books because the existing rows are deleted before inserting the dataset again.

## Aggregation SQL

### Total number of books

```sql
SELECT COUNT(*) AS total_books
FROM books;
```

### Average book price

```sql
SELECT AVG(price) AS average_price
FROM books;
```

### Top 5 most expensive books

```sql
SELECT title, price
FROM books
ORDER BY price DESC
LIMIT 5;
```

### Number of books per rating

```sql
SELECT rating, COUNT(*) AS book_count
FROM books
GROUP BY rating
ORDER BY rating;
```

## Run the API

```bash
uvicorn main:app --reload
```

The API runs at:

```text
http://127.0.0.1:8000
```

Health check:

```text
GET /health
```

## Generate a Report

Send:

```bash
curl -i -X POST http://127.0.0.1:8000/reports
```

Example response:

```json
{
  "id": 1,
  "file": "/reports/1/file"
}
```

A new report returns:

```text
201 Created
```

## Get Report Information

```text
GET /reports/{id}
```

Example:

```bash
curl http://127.0.0.1:8000/reports/1
```

## Download the PDF

```bash
curl -o my-report.pdf http://127.0.0.1:8000/reports/1/file
```

The downloaded file opens as a real PDF containing the report generated from the SQLite data.

## Synchronous Report Generation

Report generation currently happens directly inside `POST /reports`, so the request waits while Chromium creates the PDF.

For larger reports or many simultaneous users, I would move PDF generation into a background job so the API can respond immediately while the report is generated separately.

## Idempotency

Before generating a report, the API checks whether one has already been generated today. This protects against duplicate files when a user double-clicks the Generate Report button or sends the same request multiple times.

Without an idempotency check, real applications can accidentally perform costly actions more than once, such as charging a customer twice.

To deliberately generate a new report anyway, send:

```json
{
  "force": true
}
```

This skips the duplicate check and generates a new report.

## Generated PDF

![Generated PDF report](screenshots/report-page-1.png)