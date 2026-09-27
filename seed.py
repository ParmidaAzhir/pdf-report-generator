import json
import sqlite3

RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5
}

# Read the 60 scraped books
with open("books.json", "r", encoding="utf-8") as file:
    books = json.load(file)

# Create/open SQLite database
conn = sqlite3.connect("report.db")
cursor = conn.cursor()

# Create books table
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    price REAL,
    rating INTEGER,
    url TEXT
)
""")

# Clear old rows so running seed twice doesn't duplicate data
cursor.execute("DELETE FROM books")

for book in books:
    title = book["title"]

    price = book.get("price_gbp", book.get("price"))

    rating_raw = book.get("rating_text", book.get("rating"))
    rating = RATING_MAP.get(str(rating_raw), rating_raw)

    url = book.get("product_url", book.get("url"))

    cursor.execute("""
        INSERT INTO books (title, price, rating, url)
        VALUES (?, ?, ?, ?)
    """, (title, price, rating, url))

conn.commit()

cursor.execute("SELECT COUNT(*) FROM books")
count = cursor.fetchone()[0]

print("Books in database:", count)

conn.close()