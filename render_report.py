from datetime import date
from pathlib import Path
from html import escape
from playwright.sync_api import sync_playwright

from report_data import getReportData, getAllBooks


def build_html(data):
    top_rows = ""

    for book in data["top_5_expensive"]:
        top_rows += f"""
        <tr>
            <td>{escape(book["title"])}</td>
            <td>£{book["price"]:.2f}</td>
        </tr>
        """

    all_rows = ""

    for book in data["all_books"]:
        all_rows += f"""
        <tr>
            <td>{escape(book["title"])}</td>
            <td>£{book["price"]:.2f}</td>
            <td>{book["rating"]}</td>
        </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">

        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 30px;
            }}

            h1 {{
                margin-bottom: 5px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}

            th, td {{
                border: 1px solid #ccc;
                padding: 8px;
                text-align: left;
            }}

            th {{
                background: #eeeeee;
            }}

            thead {{
                display: table-header-group;
            }}

            tr {{
                break-inside: avoid;
                page-break-inside: avoid;
            }}
        </style>
    </head>

    <body>

        <h1>Bookstore Report</h1>
        <p>Date: {date.today()}</p>

        <h2>Summary</h2>

        <p><strong>Total books:</strong> {data["total_books"]}</p>
        <p><strong>Average price:</strong> £{data["average_price"]:.2f}</p>

        <h2>Top 5 Most Expensive Books</h2>

        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Price</th>
                </tr>
            </thead>

            <tbody>
                {top_rows}
            </tbody>
        </table>

        <h2>All Books</h2>

        <table>
            <thead>
                <tr>
                    <th>Title</th>
                    <th>Price</th>
                    <th>Rating</th>
                </tr>
            </thead>

            <tbody>
                {all_rows}
            </tbody>
        </table>

    </body>
    </html>
    """


def generate_pdf(path="reports/test.pdf"):
    data = getReportData()
    data["all_books"] = getAllBooks()

    html = build_html(data)

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()
        page.set_content(html)

        page.pdf(
            path=path,
            format="A4",
            print_background=True
        )

        browser.close()

    print(f"Created {path}")


if __name__ == "__main__":
    generate_pdf()