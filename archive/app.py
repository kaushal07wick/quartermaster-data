from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI()

def get_holders():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT address, usd_value FROM holders ORDER BY usd_value DESC')
    holders = cursor.fetchall()
    conn.close()
    return holders

@app.get("/", response_class=HTMLResponse)
async def display_table(request: Request):
    holders = get_holders()

    html = """
    <html>
    <head>
        <title>HYPE Holders</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #1e2d2f; color: #ffffff; padding: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th, td { padding: 10px; border: 1px solid #444; text-align: left; }
            th { background-color: #333; }
            tr:nth-child(even) { background-color: #2c3e50; }
            a { color: #00ffcc; text-decoration: none; }
        </style>
    </head>
    <body>
        <h1>HYPE Token Holders</h1>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Address</th>
                    <th>Value (USD)</th>
                </tr>
            </thead>
            <tbody>
    """

    for idx, (address, usd_value) in enumerate(holders, 1):
        html += f"""
            <tr>
                <td>{idx}</td>
                <td>{address}</td>
                <td>{usd_value:,.2f}$</td>
            </tr>
        """

    html += """
            </tbody>
        </table>
    </body>
    </html>
    """

    return HTMLResponse(content=html)
