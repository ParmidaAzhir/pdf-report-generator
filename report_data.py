import sqlite3


def getReportData():
    conn = sqlite3.connect("report.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # 1. Total number of books
    cursor.execute("SELECT COUNT(*) AS total_books FROM books")
    total_books = cursor.fetchone()["total_books"]

    # 2. Average price
    cursor.execute("SELECT AVG(price) AS average_price FROM books")
    average_price = cursor.fetchone()["average_price"]

    # 3. Top 5 most expensive books
    cursor.execute("""
        SELECT title, price
        FROM books
        ORDER BY price DESC
        LIMIT 5
    """)
    top_5 = [dict(row) for row in cursor.fetchall()]

    # 4. Number of books per rating
    cursor.execute("""
        SELECT rating, COUNT(*) AS book_count
        FROM books
        GROUP BY rating
        ORDER BY rating
    """)
    books_per_rating = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        "total_books": total_books,
        "average_price": round(average_price, 2),
        "top_5_expensive": top_5,
        "books_per_rating": books_per_rating
    }


def getAllBooks():
    conn = sqlite3.connect("report.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT title, price, rating, url
        FROM books
        ORDER BY id
    """)

    books = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return books